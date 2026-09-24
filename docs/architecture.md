# Architecture

```mermaid
sequenceDiagram
  participant D as Developer
  participant G as GitHub
  participant A as FastAPI
  participant O as Orchestrator
  participant S as SCMProvider
  participant M as Model
  D->>G: Open or update PR
  G->>A: Signed pull_request webhook
  A->>A: Verify signature, allowlist, action, draft, delivery
  A->>O: Queue isolated event context
  O->>S: PR metadata and bounded changed files
  O->>M: Policy + metadata + selected diffs
  M-->>O: Validated ReviewResult JSON
  O->>S: Idempotent summary comment
  S-->>G: Review comment
```

```mermaid
flowchart TB
  Event[Webhook event] --> Guard[Security and routing guards]
  Guard --> Context[Per-event PullRequestEvent]
  Context --> Provider[SCMProvider]
  Provider --> Github[GitHubMCPProvider]
  Github -.unattended fallback.- Rest[GitHubRESTProvider]
  Provider --> Azure[AzureDevOpsMCPProvider future]
  Context --> Diff[Diff processor]
  Diff --> Prompt[Policy prompt builder]
  Prompt --> LLM[LLM client]
  LLM --> Result[Pydantic ReviewResult]
  Result --> Format[Review formatter]
  Format --> Provider
```

The webhook event carries owner, repository, PR number, SHA, branch, and delivery ID. No PR-specific data is global. The process is concurrency-friendly for the POC and can move `background_tasks.add_task` to Azure Service Bus, RabbitMQ, Redis Queue, or Kafka without changing the review boundary.

The official GitHub MCP server is configured for VS Code in `.vscode/mcp.json`. A standalone Python webhook process does not receive the MCP host's live tool session, so REST fallback is isolated behind `GitHubMCPProvider`. An MCP SDK client can replace that adapter later.
