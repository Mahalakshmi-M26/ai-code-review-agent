import json
import logging
import os
from contextlib import AsyncExitStack
from typing import Any

from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client
from mcp.types import TextContent

from app.models import ChangedFile, PullRequestEvent

logger = logging.getLogger(__name__)


class MCPConnectionError(RuntimeError):
    pass


class MCPToolError(RuntimeError):
    pass


class GitHubMCPClient:
    def __init__(self, token: str, required_tools: set[str], command: str = "npx", args: list[str] | None = None):
        self.token = token
        self.required_tools = required_tools
        self.command = command
        self.args = args or ["-y", "@modelcontextprotocol/server-github"]
        self._stack: AsyncExitStack | None = None
        self._session: ClientSession | None = None
        self._tool_names: set[str] = set()

    @property
    def connected(self) -> bool:
        return self._session is not None

    async def connect(self) -> None:
        if self.connected:
            return
        if not self.token:
            raise MCPConnectionError("GITHUB_MCP_TOKEN is required for MCP mode")
        logger.info("github_mcp_connecting transport=stdio endpoint=local")
        stack = AsyncExitStack()
        try:
            server = StdioServerParameters(
                command=self.command,
                args=self.args,
                env={**os.environ, "GITHUB_PERSONAL_ACCESS_TOKEN": self.token},
            )
            read, write = await stack.enter_async_context(stdio_client(server))
            self._session = await stack.enter_async_context(ClientSession(read, write))
            await self._session.initialize()
            tools_result = await self._session.list_tools()
            self._tool_names = {tool.name for tool in tools_result.tools}
            missing = self.required_tools - self._tool_names
            if missing:
                raise MCPConnectionError(f"Required MCP tools are unavailable: {sorted(missing)}")
            self._stack = stack
            logger.info("github_mcp_connected")
            logger.info("github_mcp_tools_discovered count=%s", len(self._tool_names))
        except Exception as exc:
            await stack.aclose()
            self._session = None
            logger.error("github_mcp_connection_failed error_type=%s detail=%s", type(exc).__name__, str(exc)[:300])
            if isinstance(exc, MCPConnectionError):
                raise
            raise MCPConnectionError("Unable to connect to GitHub MCP Server") from exc

    async def close(self) -> None:
        if self._stack is not None:
            await self._stack.aclose()
        self._stack = None
        self._session = None
        self._tool_names.clear()

    async def list_tools(self) -> set[str]:
        await self.connect()
        return set(self._tool_names)

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        await self.connect()
        if name not in self._tool_names:
            raise MCPToolError(f"MCP tool is not available: {name}")
        assert self._session is not None
        logger.info("github_mcp_tool_call tool=%s", name)
        try:
            result = await self._session.call_tool(name, arguments)
            if result.is_error:
                raise MCPToolError(f"MCP tool returned an error: {name}")
            value = self._extract_content(result)
            logger.info("github_mcp_tool_success tool=%s", name)
            return value
        except Exception as exc:
            logger.exception("github_mcp_tool_failed tool=%s error_type=%s", name, type(exc).__name__)
            if isinstance(exc, MCPToolError):
                raise
            raise MCPToolError(f"MCP tool call failed: {name}") from exc

    @staticmethod
    def _extract_content(result: Any) -> Any:
        structured = getattr(result, "structured_content", None)
        if structured is not None:
            return structured
        text = "\n".join(block.text for block in getattr(result, "content", []) if isinstance(block, TextContent)).strip()
        if not text:
            return None
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return text


class GitHubMCPProvider:
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
