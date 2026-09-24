# MCP Integration

## Final Design

The application uses the official GitHub MCP Server as a local child process. `GitHubMCPClient` starts the configured command with `stdio_client`, creates a `ClientSession`, initializes it, discovers tools, and reuses the session for webhook reviews.

The Python service does not use a direct GitHub REST client. All GitHub reads and writes pass through MCP.

## Required Tools

The verified runtime uses:

- `get_pull_request_comments`: read comments and detect the commit marker.
- `get_pull_request_files`: retrieve changed files and patches.
- `add_issue_comment`: post the enterprise review summary.

Startup fails if a configured required tool is not discovered.

## Authentication

`GITHUB_MCP_TOKEN` is read by the Python settings layer and passed to the local MCP subprocess as `GITHUB_PERSONAL_ACCESS_TOKEN`. Keep the token in `.env` or an approved secret manager. Never put it in source, documentation, or logs.

## Configuration

```text
GITHUB_MCP_TOKEN=replace-with-github-mcp-token
GITHUB_MCP_TOOLS=get_pull_request_comments,get_pull_request_files,add_issue_comment
GITHUB_MCP_COMMAND=npx
GITHUB_MCP_ARGS=-y @modelcontextprotocol/server-github
```

`GITHUB_MCP_ARGS` is parsed with shell-style argument rules. The local machine therefore needs Node.js and `npx` available on `PATH`.

## Why Local Stdio

The POC needs a service-owned MCP session for unattended webhook processing. Local stdio keeps the MCP process beside the FastAPI process and avoids relying on a separate interactive host session.

## Runtime Evidence

The application logs the following non-secret lifecycle evidence:

```text
github_mcp_connecting transport=stdio endpoint=local
github_mcp_connected
github_mcp_tools_discovered count=...
github_mcp_tool_call tool=get_pull_request_files
github_mcp_tool_success tool=get_pull_request_files
```

## Error Handling

The client fails startup when the token is missing, the subprocess cannot initialize, or required tools are unavailable. Tool errors are raised as `MCPToolError` and the webhook task logs the failed review without posting an unvalidated result.
