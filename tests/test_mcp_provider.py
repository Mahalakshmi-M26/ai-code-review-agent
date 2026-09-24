import pytest

from app.mcp import github_client as client_module
from app.mcp.github_client import GitHubMCPClient, MCPToolError
from app.models.webhook import PullRequestEvent
from app.scm.github_mcp import GitHubMCPProvider


class FakeTool:
    def __init__(self, name):
        self.name = name


class FakeToolResult:
    def __init__(self, value, is_error=False):
        self.structured_content = value
        self.content = []
        self.is_error = is_error


class FakeMCPClient:
    def __init__(self, transport):
        self.calls = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, traceback):
        return False

    async def list_tools(self):
        return type("Tools", (), {"tools": [FakeTool("pull_request_read"), FakeTool("add_issue_comment")]})()

    async def call_tool(self, name, arguments):
        self.calls.append((name, arguments))
        if name == "pull_request_read" and arguments["method"] == "get_files":
            return FakeToolResult({"files": [{"filename": "app.py", "status": "modified", "patch": "+print('x')"}]})
        if name == "pull_request_read" and arguments["method"] == "get_comments":
            return FakeToolResult({"comments": [{"body": "<!-- ai-code-review-agent:sha -->"}]})
        return FakeToolResult({"ok": True})


class FakeTransport:
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, traceback):
        return False


@pytest.mark.asyncio
async def test_mcp_client_connects_discovers_tools_and_closes(monkeypatch):
    monkeypatch.setattr(client_module, "Client", FakeMCPClient)
    monkeypatch.setattr(client_module, "streamable_http_client", lambda url, http_client: FakeTransport())
    client = GitHubMCPClient("https://example.test/mcp", "token", {"pull_request_read", "add_issue_comment"})
    await client.connect()
    assert client.connected
    assert await client.list_tools() == {"pull_request_read", "add_issue_comment"}
    await client.close()
    assert not client.connected


@pytest.mark.asyncio
async def test_mcp_client_supports_stdio_transport(monkeypatch):
    captured = {}

    class FakeSession:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, traceback):
            return False

        async def initialize(self):
            captured["initialized"] = True

        async def list_tools(self):
            return type("Tools", (), {"tools": [FakeTool("pull_request_read")]})()

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
    client = GitHubMCPClient(
        "unused",
        "token",
        {"pull_request_read"},
        transport="stdio",
        command="npx",
        args=["-y", "server"],
    )

    await client.connect()
    assert client.connected
    assert captured["initialized"]
    assert captured["server"].command == "npx"
    assert captured["server"].args == ["-y", "server"]
    assert captured["server"].env["GITHUB_PERSONAL_ACCESS_TOKEN"] == "token"
    await client.call_tool("pull_request_read", {"owner": "o"})
    assert captured["call"] == ("pull_request_read", {"owner": "o"})
    await client.close()
    assert not client.connected


@pytest.mark.asyncio
async def test_provider_uses_mcp_for_files_comments_and_post():
    class DirectMCPClient:
        def __init__(self):
            self.calls = []

        async def call_tool(self, name, arguments):
            self.calls.append((name, arguments))
            if name == "pull_request_read" and arguments["method"] == "get_files":
                return {"files": [{"filename": "app.py", "status": "modified", "patch": "+print('x')"}]}
            if name == "pull_request_read" and arguments["method"] == "get_comments":
                return {"comments": [{"body": "<!-- ai-code-review-agent:sha -->"}]}
            return {"ok": True}

    client = DirectMCPClient()
    provider = GitHubMCPProvider(client)
    event = PullRequestEvent(action="opened", repository="repo-a", owner="owner", pr_number=7, commit_sha="sha", branch="main")

    files = await provider.get_changed_files(event)
    assert files[0].path == "app.py"
    assert await provider.has_review_marker(event, "<!-- ai-code-review-agent:sha -->")
    await provider.post_review(event, "review body")
    assert [call[0] for call in client.calls] == ["pull_request_read", "pull_request_read", "add_issue_comment"]


@pytest.mark.asyncio
async def test_provider_supports_legacy_stdio_tools():
    class LegacyClient:
        def __init__(self):
            self.calls = []

        async def list_tools(self):
            return {"get_pull_request_files", "create_pull_request_review"}

        async def call_tool(self, name, arguments):
            self.calls.append((name, arguments))
            if name == "get_pull_request_files":
                return [{"filename": "app.py", "status": "modified", "patch": "+print('x')"}]
            return {"ok": True}

    client = LegacyClient()
    provider = GitHubMCPProvider(client)
    event = PullRequestEvent(action="opened", repository="repo-a", owner="owner", pr_number=7, commit_sha="sha", branch="main")

    files = await provider.get_changed_files(event)
    await provider.post_review(event, "review body")
    assert files[0].path == "app.py"
    assert client.calls == [
        ("get_pull_request_files", {"owner": "owner", "repo": "repo-a", "pull_number": 7}),
        ("create_pull_request_review", {"owner": "owner", "repo": "repo-a", "pull_number": 7, "body": "review body", "event": "COMMENT"}),
    ]


@pytest.mark.asyncio
async def test_mcp_failure_does_not_use_rest_when_fallback_disabled():
    class FailingClient:
        async def call_tool(self, name, arguments):
            raise MCPToolError("failed")

    class FailingREST:
        async def get_changed_files(self, event):
            raise AssertionError("REST fallback must not be called")

    client = FailingClient()
    provider = GitHubMCPProvider(client, FailingREST(), allow_rest_fallback=False)
    event = PullRequestEvent(action="opened", repository="repo-a", owner="owner", pr_number=7, commit_sha="sha", branch="main")
    with pytest.raises(MCPToolError):
        await provider.get_changed_files(event)