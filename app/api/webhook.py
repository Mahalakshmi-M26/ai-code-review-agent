import json
import logging
from fastapi import APIRouter, BackgroundTasks, Header, HTTPException, Request
from app.core.config import get_settings
from app.core.security import verify_github_signature
from app.llm.client import LLMClient
from app.mcp.github_client import GitHubMCPClient
from app.models.webhook import PullRequestEvent
from app.scm.github_mcp import GitHubMCPProvider
from app.services.orchestrator import ReviewOrchestrator

router = APIRouter()
logger = logging.getLogger(__name__)
RELEVANT_ACTIONS = {"opened", "reopened", "synchronize", "ready_for_review"}
_seen_deliveries: set[str] = set()


def build_orchestrator(request: Request | None = None) -> ReviewOrchestrator:
    settings = get_settings()
    if request is None or not hasattr(request.app.state, "github_mcp_client"):
        raise RuntimeError("GitHub MCP client is not initialized")
    mcp_client: GitHubMCPClient = request.app.state.github_mcp_client
    scm = GitHubMCPProvider(mcp_client)
    llm = LLMClient(settings.openai_base_url, settings.gep_api_key, settings.model_name, settings.review_timeout_seconds, settings.mock_external_services)
    return ReviewOrchestrator(settings, scm, llm)


async def run_review(orchestrator: ReviewOrchestrator, event: PullRequestEvent) -> None:
    try:
        result = await orchestrator.process(event)
        logger.info("review_finished repository=%s pr=%s commit_sha=%s result=%s", event.full_name, event.pr_number, event.commit_sha, result)
    except Exception:
        logger.exception("review_failed repository=%s pr=%s commit_sha=%s", event.full_name, event.pr_number, event.commit_sha)


@router.post("/webhooks/github", status_code=202)
@router.post("/webhook/github", status_code=202, include_in_schema=False)
async def github_webhook(request: Request, background_tasks: BackgroundTasks, x_hub_signature_256: str | None = Header(default=None), x_github_event: str | None = Header(default=None), x_github_delivery: str | None = Header(default=None)) -> dict:
    settings = get_settings()
    raw = await request.body()
    if not verify_github_signature(raw, x_hub_signature_256, settings.github_webhook_secret):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")
    if x_github_event != "pull_request":
        return {"status": "ignored", "reason": "unsupported event"}
    delivery_id = x_github_delivery or "unknown"
    if delivery_id in _seen_deliveries:
        return {"status": "ignored", "reason": "duplicate delivery"}
    try:
        payload = json.loads(raw)
        event = PullRequestEvent.from_github_payload(payload, delivery_id)
    except (ValueError, TypeError, KeyError) as exc:
        raise HTTPException(status_code=400, detail="Malformed GitHub payload") from exc
    if event.action not in RELEVANT_ACTIONS:
        return {"status": "ignored", "reason": f"action {event.action} is not reviewable"}
    if not settings.repository_allowed(event.full_name):
        raise HTTPException(status_code=403, detail="Repository is not authorized")
    if event.draft and not settings.allow_draft_reviews:
        return {"status": "ignored", "reason": "draft pull request"}
    _seen_deliveries.add(delivery_id)
    background_tasks.add_task(run_review, build_orchestrator(request), event)
    logger.info("review_queued repository=%s pr=%s commit_sha=%s", event.full_name, event.pr_number, event.commit_sha)
    return {"status": "queued", "repository": event.full_name, "pr_number": event.pr_number}
