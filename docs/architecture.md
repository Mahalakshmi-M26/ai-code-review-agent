# Final Architecture

## Runtime Boundaries

- **Webhook transport:** HTTP from GitHub, exposed locally through ngrok.
- **Application:** FastAPI receives, authenticates, filters, and queues pull-request events.
- **GitHub integration:** MCP only, through `GitHubMCPProvider` and `GitHubMCPClient`.
- **MCP transport:** Local stdio process started by the Python application.
- **AI inference:** HTTP request to the Capgemini Generative Engine.
- **Review action:** MCP `add_issue_comment` posts the formatted result.

## System Architecture

```mermaid
flowchart TB
  GitHub[GitHub Pull Request] -->|signed HTTP webhook| Ngrok[ngrok]
  Ngrok --> FastAPI[FastAPI]
  FastAPI --> Guard[HMAC and repository guards]
  Guard --> Orchestrator[ReviewOrchestrator]
  Orchestrator --> Provider[GitHubMCPProvider]
  Provider --> Client[GitHubMCPClient]
  Client -->|stdio| LocalMCP[Local GitHub MCP Server]
  LocalMCP --> GitHub
  Orchestrator --> Policy[enterprise_review.md]
  Orchestrator --> Prompt[PromptBuilder]
  Prompt --> Engine[Capgemini Generative Engine HTTP API]
  Engine --> Validation[Pydantic ReviewResult]
  Validation --> Formatter[Enterprise Review Formatter]
  Formatter --> Client
```

## Pull-Request Sequence

```mermaid
sequenceDiagram
  participant G as GitHub
  participant N as ngrok
  participant A as FastAPI
  participant O as Orchestrator
  participant M as Local MCP
  participant E as Generative Engine
  G->>N: pull_request webhook
  N->>A: HTTP request
  A->>A: HMAC, action, repository, draft checks
  A->>O: Background review event
  O->>M: get_pull_request_comments
  M-->>O: Existing PR comments
  O->>O: Commit marker check
  O->>M: get_pull_request_files
  M-->>O: Changed files
  O->>E: Policy, metadata, bounded diffs
  E-->>O: JSON review
  O->>O: Pydantic validation and formatting
  O->>M: add_issue_comment
  M-->>G: Review summary comment
```

## MCP Flow

```mermaid
flowchart LR
  Startup[FastAPI lifespan] --> Session[ClientSession]
  Session -->|stdio| Server[Local GitHub MCP Server]
  Server --> Discovery[list_tools]
  Discovery --> Required[Required tool check]
  Required --> Comments[get_pull_request_comments]
  Required --> Files[get_pull_request_files]
  Required --> Comment[add_issue_comment]
```

The required tool set is configured by `GITHUB_MCP_TOOLS`. The verified demo set is `get_pull_request_comments,get_pull_request_files,add_issue_comment`.

## Multi-Repository Flow

```mermaid
flowchart LR
  Events[PR events from multiple repositories] --> Webhook[Single webhook endpoint]
  Webhook --> Event[PullRequestEvent per delivery]
  Event --> Allowlist[ALLOWED_REPOSITORIES check]
  Allowlist --> Review[Independent review context]
  Review --> Repository[owner/repository MCP arguments]
```

No repository-specific state is stored in the orchestrator. Each event carries its own owner, repository, PR number, branch, commit SHA, and delivery ID.

## Health Endpoint

`GET /health` returns a simple service status. It does not replace MCP startup validation; the application startup waits for MCP connection and required-tool discovery.
