import logging

from app.models.webhook import PullRequestEvent
from app.mcp.github_client import GitHubMCPClient
from app.scm.base import ChangedFile, SCMProvider
from app.scm.github_rest import GitHubRESTProvider

logger = logging.getLogger(__name__)


class GitHubMCPProvider(SCMProvider):
    """SCM boundary backed by the official GitHub MCP Server."""

    def __init__(self, client: GitHubMCPClient, rest_fallback: GitHubRESTProvider | None = None, allow_rest_fallback: bool = False):
        self.client = client
        self.rest_fallback = rest_fallback
        self.allow_rest_fallback = allow_rest_fallback

    async def _available_tools(self) -> set[str] | None:
        list_tools = getattr(self.client, "list_tools", None)
        return await list_tools() if list_tools is not None else None

    async def _call(self, method: str, event: PullRequestEvent, arguments: dict, fallback_method: str, legacy_method: str | None = None, legacy_arguments: dict | None = None):
        try:
            tool_names = await self._available_tools()
            selected_method = method
            selected_arguments = arguments
            if tool_names is not None and method not in tool_names:
                if legacy_method is None or legacy_method not in tool_names:
                    raise RuntimeError(f"Neither MCP tool is available: {method}, {legacy_method}")
                selected_method = legacy_method
                selected_arguments = legacy_arguments or arguments
            return await self.client.call_tool(selected_method, selected_arguments)
        except Exception:
            if not self.allow_rest_fallback or self.rest_fallback is None:
                raise
            logger.warning("github_rest_fallback_used operation=%s", fallback_method)
            return await getattr(self.rest_fallback, fallback_method)(event)

    async def get_pull_request(self, event: PullRequestEvent) -> dict:
        return await self._call(
            "pull_request_read",
            event,
            {"method": "get", "owner": event.owner, "repo": event.repository, "pullNumber": event.pr_number},
            "get_pull_request",
            "get_pull_request",
            {"owner": event.owner, "repo": event.repository, "pull_number": event.pr_number},
        )

    async def get_changed_files(self, event: PullRequestEvent) -> list[ChangedFile]:
        result = await self._call(
            "pull_request_read",
            event,
            {"method": "get_files", "owner": event.owner, "repo": event.repository, "pullNumber": event.pr_number, "perPage": 100},
            "get_changed_files",
            "get_pull_request_files",
            {"owner": event.owner, "repo": event.repository, "pull_number": event.pr_number},
        )
        entries = result.get("files", result) if isinstance(result, dict) else result
        return [ChangedFile(item["filename"], item.get("status", "modified"), item.get("patch") or "", item.get("patch") is None) for item in entries or []]

    async def get_pull_request_diff(self, event: PullRequestEvent):
        return await self._call("pull_request_read", event, {"method": "get_diff", "owner": event.owner, "repo": event.repository, "pullNumber": event.pr_number}, "get_pull_request_diff")

    async def post_review(self, event: PullRequestEvent, body: str) -> None:
        await self._call(
            "add_issue_comment",
            event,
            {"owner": event.owner, "repo": event.repository, "issue_number": event.pr_number, "body": body},
            "post_review",
            "create_pull_request_review",
            {"owner": event.owner, "repo": event.repository, "pull_number": event.pr_number, "body": body, "event": "COMMENT"},
        )

    async def has_review_marker(self, event: PullRequestEvent, marker: str) -> bool:
        tool_names = await self._available_tools()
        if tool_names is not None and "pull_request_read" not in tool_names:
            legacy_comments = next((name for name in ("get_pull_request_comments", "get_issue_comments") if name in tool_names), None)
            if legacy_comments is None:
                logger.warning("github_mcp_marker_check_unavailable legacy_server=true")
                return False
            result = await self.client.call_tool(
                legacy_comments,
                {"owner": event.owner, "repo": event.repository, "pull_number": event.pr_number},
            )
            comments = result.get("comments", result) if isinstance(result, dict) else result
            return any(marker in item.get("body", "") for item in comments or [])
        result = await self._call("pull_request_read", event, {"method": "get_comments", "owner": event.owner, "repo": event.repository, "pullNumber": event.pr_number, "perPage": 100}, "has_review_marker")
        comments = result.get("comments", result) if isinstance(result, dict) else result
        return any(marker in item.get("body", "") for item in comments or [])
