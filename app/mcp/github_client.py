import json
import logging
import os
from contextlib import AsyncExitStack
from typing import Any

import httpx2
from mcp import Client, ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client
from mcp.client.streamable_http import streamable_http_client
from mcp.types import TextContent

logger = logging.getLogger(__name__)


class MCPConnectionError(RuntimeError):
    pass


class MCPToolError(RuntimeError):
    pass


class GitHubMCPClient:
    def __init__(self, url: str, token: str, required_tools: set[str], timeout: float = 60, transport: str = "http", command: str = "npx", args: list[str] | None = None):
        self.url = url
        self.token = token
        self.required_tools = required_tools
        self.timeout = timeout
        self.transport = transport.lower()
        self.command = command
        self.args = args or ["-y", "@modelcontextprotocol/server-github"]
        self._stack: AsyncExitStack | None = None
        self._client: Client | None = None
        self._session: ClientSession | None = None
        self._tool_names: set[str] = set()

    @property
    def connected(self) -> bool:
        return self._client is not None or self._session is not None

    async def connect(self) -> None:
        if self.connected:
            return
        if not self.token:
            raise MCPConnectionError("GITHUB_MCP_TOKEN is required for MCP mode")
        logger.info("github_mcp_connecting transport=%s endpoint=%s", self.transport, self.url if self.transport == "http" else "local")
        stack = AsyncExitStack()
        try:
            if self.transport == "http":
                http_client = await stack.enter_async_context(
                    httpx2.AsyncClient(
                        headers={
                            "Authorization": f"Bearer {self.token}",
                            "X-MCP-Tools": ",".join(sorted(self.required_tools)),
                        },
                        timeout=httpx2.Timeout(self.timeout, read=self.timeout),
                    )
                )
                transport = streamable_http_client(self.url, http_client=http_client)
                client = await stack.enter_async_context(Client(transport))
                self._client = client
            elif self.transport == "stdio":
                server = StdioServerParameters(
                    command=self.command,
                    args=self.args,
                    env={**os.environ, "GITHUB_PERSONAL_ACCESS_TOKEN": self.token},
                )
                read, write = await stack.enter_async_context(stdio_client(server))
                self._session = await stack.enter_async_context(ClientSession(read, write))
                await self._session.initialize()
            else:
                raise MCPConnectionError("GITHUB_MCP_TRANSPORT must be http or stdio")
            connected_client = self._client or self._session
            assert connected_client is not None
            tools_result = await connected_client.list_tools()
            self._tool_names = {tool.name for tool in tools_result.tools}
            missing = self.required_tools - self._tool_names
            if missing:
                raise MCPConnectionError(f"Required MCP tools are unavailable: {sorted(missing)}")
            self._stack = stack
            logger.info("github_mcp_connected")
            logger.info("github_mcp_tools_discovered count=%s", len(self._tool_names))
        except Exception as exc:
            await stack.aclose()
            logger.error("github_mcp_connection_failed error_type=%s detail=%s", type(exc).__name__, self._safe_error(exc))
            if isinstance(exc, MCPConnectionError):
                raise
            raise MCPConnectionError("Unable to connect to GitHub MCP Server") from exc

    @staticmethod
    def _safe_error(exc: Exception) -> str:
        message = str(exc)
        if "web-notification.capgemini.com" in message:
            return "Hosted MCP endpoint was redirected by the corporate network; check corporate proxy or use an approved direct endpoint"
        return message[:300]

    async def close(self) -> None:
        if self._stack is not None:
            await self._stack.aclose()
        self._stack = None
        self._client = None
        self._session = None
        self._tool_names.clear()

    async def list_tools(self) -> set[str]:
        await self.connect()
        return set(self._tool_names)

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        await self.connect()
        if name not in self._tool_names:
            raise MCPToolError(f"MCP tool is not available: {name}")
        connected_client = self._client or self._session
        assert connected_client is not None
        logger.info("github_mcp_tool_call tool=%s", name)
        try:
            result = await connected_client.call_tool(name, arguments)
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
        text_parts = [block.text for block in getattr(result, "content", []) if isinstance(block, TextContent)]
        text = "\n".join(text_parts).strip()
        if not text:
            return None
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return text