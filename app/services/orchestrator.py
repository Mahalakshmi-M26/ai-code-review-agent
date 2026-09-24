import hashlib
import logging
from app.core.config import Settings
from app.llm.client import LLMClient
from app.models.webhook import PullRequestEvent
from app.scm.base import SCMProvider
from app.services.diff_processor import prepare_files
from app.services.prompt_builder import PromptBuilder
from app.services.review_formatter import format_review

logger = logging.getLogger(__name__)


class ReviewOrchestrator:
    def __init__(self, settings: Settings, scm: SCMProvider, llm: LLMClient):
        self.settings, self.scm, self.llm = settings, scm, llm
        self.prompt_builder = PromptBuilder(settings.policy_path)

    async def process(self, event: PullRequestEvent) -> str:
        marker = f"<!-- ai-code-review-agent:{event.commit_sha} -->"
        if await self.scm.has_review_marker(event, marker):
            return "duplicate"
        files = await self.scm.get_changed_files(event)
        selected, skipped = prepare_files(files, self.settings.max_files, self.settings.max_file_diff_chars, self.settings.max_review_input_chars)
        result = await self.llm.review(self.prompt_builder.build(event, selected))
        result.files_reviewed, result.files_skipped = len(selected), skipped
        body = format_review(result, marker)
        await self.scm.post_review(event, body)
        logger.info("review_posted repository=%s pr=%s commit_sha=%s", event.full_name, event.pr_number, event.commit_sha)
        return "posted"


def delivery_correlation_id(delivery_id: str, event: PullRequestEvent) -> str:
    return hashlib.sha256(f"{delivery_id}:{event.full_name}:{event.pr_number}:{event.commit_sha}".encode()).hexdigest()[:16]
