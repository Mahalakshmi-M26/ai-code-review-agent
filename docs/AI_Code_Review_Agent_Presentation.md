# AI Code Review Agent Presentation

## Slide 1: AI Code Review Agent

**Bullets**
- MCP-based pull-request review POC
- Enterprise policy plus Generative Engine
- Human-governed review comments

**Recommended visual:** Title over the final architecture flow.

**Speaker notes:** This demo shows a working end-to-end local integration, not an autonomous merge bot.

## Slide 2: Problem Statement

**Bullets**
- Review effort is repetitive
- Standards vary by reviewer
- Full repositories should not be sent to a model

**Recommended visual:** PR change set with risk categories.

**Speaker notes:** The goal is consistent assistance while keeping engineers in control.

## Slide 3: Proposed Solution

**Bullets**
- Signed webhook trigger
- MCP retrieval and posting
- Policy-constrained structured review

**Recommended visual:** Three-stage observe, reason, act diagram.

**Speaker notes:** Each stage has a clear security and ownership boundary.

## Slide 4: Agent Workflow

**Bullets**
- Receive and authenticate event
- Check idempotency
- Retrieve bounded diffs
- Analyze, validate, and comment

**Recommended visual:** Sequence diagram.

**Speaker notes:** The orchestrator coordinates the workflow without knowing GitHub transport details.

## Slide 5: Enterprise Architecture

**Bullets**
- GitHub webhook over HTTP
- FastAPI and background task
- Local stdio MCP
- Generative Engine over HTTP

**Recommended visual:** System architecture Mermaid diagram.

**Speaker notes:** Do not confuse webhook HTTP or inference HTTP with GitHub integration; GitHub operations are MCP-only.

## Slide 6: Technology Stack

**Bullets**
- Python, FastAPI, Uvicorn
- MCP Python SDK
- Local official GitHub MCP Server
- Pydantic and pytest
- ngrok for demo ingress

**Recommended visual:** Technology stack layers.

**Speaker notes:** The stack is intentionally small enough to explain live.

## Slide 7: GitHub MCP Integration

**Bullets**
- `get_pull_request_comments`
- `get_pull_request_files`
- `add_issue_comment`
- Startup discovery verifies the contract

**Recommended visual:** Tool catalog connected to the provider.

**Speaker notes:** Logs provide direct evidence that these tools are invoked.

## Slide 8: MCP Runtime Flow

**Bullets**
- Python starts local process
- Token becomes child-process environment
- ClientSession initializes
- Tools are discovered before serving

**Recommended visual:** Python process to stdio server diagram.

**Speaker notes:** Local stdio avoids depending on an interactive IDE session.

## Slide 9: Capgemini Generative Engine

**Bullets**
- OpenAI-compatible chat completions
- Policy and bounded diffs as input
- JSON response required

**Recommended visual:** Prompt-to-structured-response flow.

**Speaker notes:** The model performs analysis; it does not access GitHub directly.

## Slide 10: Enterprise Review Standard

**Bullets**
- Markdown policy file
- Severity and evidence guidance
- Security, architecture, and testing categories
- Human approval remains mandatory

**Recommended visual:** Policy document beside review categories.

**Speaker notes:** Markdown keeps governance visible and editable.

## Slide 11: Enterprise Review Output

**Bullets**
- Decision and risk level
- Severity counts
- Evidence-based findings
- Remediation and commit marker

**Recommended visual:** Screenshot or mock-up of the PR comment.

**Speaker notes:** The formatter turns validated data into a consistent stakeholder-facing comment.

## Slide 12: Security

**Bullets**
- HMAC-SHA256 validation
- Repository allowlist
- Secret isolation
- Prompt-injection boundary
- No auto-merge

**Recommended visual:** Security control checkpoints.

**Speaker notes:** The POC is deliberately conservative about actions and untrusted input.

## Slide 13: Multi-Repository Support

**Bullets**
- Owner and repository from each event
- `ALLOWED_REPOSITORIES` policy
- Independent event context
- Wildcard only for controlled demos

**Recommended visual:** Multiple repositories converging on one webhook.

**Speaker notes:** Production should use explicit authorization rather than `*`.

## Slide 14: Live Demo and Production Evolution

**Bullets**
- Start FastAPI and ngrok
- Open or update a PR
- Show MCP logs and posted comment
- Evolve to durable queue and idempotency

**Recommended visual:** Terminal plus GitHub PR.

**Speaker notes:** First prove the current flow, then explain the production hardening path.

## Slide 15: Conclusion and Q&A

**Bullets**
- Working MCP-based POC
- Governed, bounded AI review
- Clear extension point for Azure DevOps MCP

**Recommended visual:** Final flow with human reviewer at the decision boundary.

**Speaker notes:** Invite questions about MCP, security, scale, and governance.
