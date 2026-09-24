# MCP Integration

This project uses the official GitHub MCP Server from `github/github-mcp-server`, not an old npm package. The FastAPI process uses the official MCP Python SDK over remote Streamable HTTP at `https://api.githubcopilot.com/mcp/`. Docker, Docker Desktop, local containers, and npx are not required. `.vscode/mcp.json` remains separate VS Code/Copilot host configuration.

The same client supports local stdio when `GITHUB_MCP_TRANSPORT=stdio`. Configure `GITHUB_MCP_COMMAND` and `GITHUB_MCP_ARGS`; the token is supplied to the child process as `GITHUB_PERSONAL_ACCESS_TOKEN`. The server must expose `pull_request_read` and `add_issue_comment` (or the names listed in `GITHUB_MCP_TOOLS`). The older npm sample with `get_pull_request` and `create_pull_request_review` uses a different tool contract and is not a drop-in replacement.

MCP is the tool contract and discovery layer used by Copilot and other compatible hosts. The webhook service creates its own SDK `Client`, calls `list_tools()` at application startup, and calls `call_tool()` for PR operations. REST remains available only when `GITHUB_REST_FALLBACK=true`.

For production, choose one of these patterns:

- Run the service-side MCP client with a managed GitHub App identity or approved PAT.
- Keep the isolated REST fallback disabled for the Phase 1 proof of MCP execution.
- Use `pull_request_read` for PR metadata, files, diffs, and comments.
- Use `add_issue_comment` for the enterprise summary comment.

Azure DevOps can implement the same `SCMProvider` methods without changing the orchestrator.
