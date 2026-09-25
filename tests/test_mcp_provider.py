import pytest

from app import github_mcp as client_module
from app.github_mcp import GitHubMCPClient, GitHubMCPProvider, MCPToolError
from app.models import PullRequestEvent


class FakeTool:
    def __init__(self, name):
        self.name = name


class FakeToolResult:
    def __init__(self, value, is_error=False):
        self.structured_content = value
        self.content = []
        self.is_error = is_error


@pytest.mark.asyncio
async def test_mcp_client_connects_discovers_tools_and_closes(monkeypatch):
    captured = {}

    class FakeSession:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, traceback):
            return False

        async def initialize(self):
            captured["initialized"] = True

        async def list_tools(self):
            return type("Tools", (), {"tools": [FakeTool("get_pull_request_files")]})()

        async def call_tool(self, name, arguments):
            captured["call"] = (name, arguments)
            return FakeToolResult({"ok": True})

    class FakeStdioContext:
        async def __aenter__(self):
            return object(), object()

        async def __aexit__(self, exc_type, exc, traceback):
            return False

    def fake_stdio_client(server):
        captured["server"] = server
        return FakeStdioContext()

    monkeypatch.setattr(client_module, "stdio_client", fake_stdio_client)
    monkeypatch.setattr(client_module, "ClientSession", lambda read, write: FakeSession())
    client = GitHubMCPClient("token", {"get_pull_request_files"}, command="npx", args=["-y", "server"])

    await client.connect()
    assert client.connected
    assert captured["initialized"]
    assert captured["server"].command == "npx"
    assert captured["server"].args == ["-y", "server"]
    assert captured["server"].env["GITHUB_PERSONAL_ACCESS_TOKEN"] == "token"
    assert await client.list_tools() == {"get_pull_request_files"}
    await client.call_tool("get_pull_request_files", {"owner": "o"})
    assert captured["call"] == ("get_pull_request_files", {"owner": "o"})
    await client.close()
    assert not client.connected


@pytest.mark.asyncio
async def test_provider_uses_verified_mcp_tools_for_files_comments_and_post():
    class DirectMCPClient:
        def __init__(self):
            self.calls = []

        async def call_tool(self, name, arguments):
            self.calls.append((name, arguments))
            if name == "get_pull_request_files":
                return {"files": [{"filename": "app.py", "status": "modified", "patch": "+print('x')"}]}
            if name == "get_pull_request_comments":
                return {"comments": [{"body": "<!-- ai-code-review-agent:sha -->"}]}
            return {"ok": True}

    client = DirectMCPClient()
    provider = GitHubMCPProvider(client)
    event = PullRequestEvent(action="opened", repository="repo-a", owner="owner", pr_number=7, commit_sha="sha", branch="main")

    files = await provider.get_changed_files(event)
    assert files[0].path == "app.py"
    assert await provider.has_review_marker(event, "<!-- ai-code-review-agent:sha -->")
    await provider.post_review(event, "review body")
    assert [call[0] for call in client.calls] == ["get_pull_request_files", "get_pull_request_comments", "add_issue_comment"]


@pytest.mark.asyncio
async def test_mcp_failure_is_propagated():
    class FailingClient:
        async def call_tool(self, name, arguments):
            raise MCPToolError("failed")

    provider = GitHubMCPProvider(FailingClient())
    event = PullRequestEvent(action="opened", repository="repo-a", owner="owner", pr_number=7, commit_sha="sha", branch="main")
    with pytest.raises(MCPToolError):
        await provider.get_changed_files(event)