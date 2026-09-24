from app.models.webhook import PullRequestEvent
from app.scm.base import ChangedFile, SCMProvider


class AzureDevOpsMCPProvider(SCMProvider):
    """Future provider seam; Azure DevOps credentials and APIs are intentionally not assumed."""

    async def get_pull_request(self, event: PullRequestEvent) -> dict:
        raise NotImplementedError("Azure DevOps MCP provider is reserved for a future adapter")

    async def get_changed_files(self, event: PullRequestEvent) -> list[ChangedFile]:
        raise NotImplementedError

    async def post_review(self, event: PullRequestEvent, body: str) -> None:
        raise NotImplementedError

    async def has_review_marker(self, event: PullRequestEvent, marker: str) -> bool:
        raise NotImplementedError
