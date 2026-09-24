import httpx
from app.models.webhook import PullRequestEvent
from app.scm.base import ChangedFile, SCMProvider


class GitHubRESTProvider(SCMProvider):
    def __init__(self, token: str, timeout: float = 30):
        self.client = httpx.AsyncClient(
            base_url="https://api.github.com",
            timeout=timeout,
            headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"},
        )

    async def get_pull_request(self, event: PullRequestEvent) -> dict:
        response = await self.client.get(f"/repos/{event.full_name}/pulls/{event.pr_number}")
        response.raise_for_status()
        return response.json()

    async def get_changed_files(self, event: PullRequestEvent) -> list[ChangedFile]:
        response = await self.client.get(f"/repos/{event.full_name}/pulls/{event.pr_number}/files", params={"per_page": 100})
        response.raise_for_status()
        return [ChangedFile(item["filename"], item.get("status", "modified"), item.get("patch") or "", item.get("patch") is None) for item in response.json()]

    async def post_review(self, event: PullRequestEvent, body: str) -> None:
        response = await self.client.post(f"/repos/{event.full_name}/issues/{event.pr_number}/comments", json={"body": body})
        response.raise_for_status()

    async def has_review_marker(self, event: PullRequestEvent, marker: str) -> bool:
        response = await self.client.get(f"/repos/{event.full_name}/issues/{event.pr_number}/comments", params={"per_page": 100})
        response.raise_for_status()
        return any(marker in item.get("body", "") for item in response.json())
