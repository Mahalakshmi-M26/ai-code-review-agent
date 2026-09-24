import logging

from app.models.webhook import PullRequestEvent
from app.mcp.github_client import GitHubMCPClient
from app.scm.base import ChangedFile, SCMProvider

logger = logging.getLogger(__name__)


class GitHubMCPProvider(SCMProvider):
    """SCM boundary backed by the official GitHub MCP Server."""

    def __init__(self, client: GitHubMCPClient):
        self.client = client

    async def get_changed_files(self, event: PullRequestEvent) -> list[ChangedFile]:
        result = await self.client.call_tool("get_pull_request_files", {"owner": event.owner, "repo": event.repository, "pull_number": event.pr_number})
        entries = result.get("files", result) if isinstance(result, dict) else result
        return [ChangedFile(item["filename"], item.get("status", "modified"), item.get("patch") or "", item.get("patch") is None) for item in entries or []]

    async def post_review(self, event: PullRequestEvent, body: str) -> None:
        await self.client.call_tool("add_issue_comment", {"owner": event.owner, "repo": event.repository, "issue_number": event.pr_number, "body": body})

    async def has_review_marker(self, event: PullRequestEvent, marker: str) -> bool:
        result = await self.client.call_tool("get_pull_request_comments", {"owner": event.owner, "repo": event.repository, "pull_number": event.pr_number})
        comments = result.get("comments", result) if isinstance(result, dict) else result
        return any(marker in item.get("body", "") for item in comments or [])
