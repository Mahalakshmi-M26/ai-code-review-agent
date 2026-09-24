# 10-15 Minute Demo Guide

Keep `.env` values hidden. Start Uvicorn and ngrok before the live portion.

## 1. README.md

**WHAT TO SHOW:** The problem, architecture diagram, and runtime flow.

**WHAT TO SAY:** This agent receives a signed PR event, uses MCP for GitHub operations, sends bounded context to the Generative Engine, validates the result, and posts a governed comment.

**WHY IT MATTERS:** Establishes the complete story before opening implementation files.

**POSSIBLE MENTOR QUESTION:** Where is MCP used? Answer: every GitHub read and write passes through the local MCP server.

## 2. app/main.py

**WHAT TO SHOW:** Lifespan startup, MCP client construction, connection, cleanup, and `/health`.

**WHAT TO SAY:** The application does not accept reviews until local MCP connects and required tools are discovered.

**WHY IT MATTERS:** Proves MCP is service-owned and not an interactive IDE dependency.

**POSSIBLE MENTOR QUESTION:** What happens if MCP is unavailable? Answer: startup fails closed.

## 3. app/api/webhook.py

**WHAT TO SHOW:** Signature verification, event filtering, repository authorization, draft handling, delivery tracking, and background task.

**WHAT TO SAY:** The handler authenticates and routes the event; it does not contain review logic.

**WHY IT MATTERS:** Shows the security and request-boundary controls.

**POSSIBLE MENTOR QUESTION:** Which PR actions are processed? Answer: opened, reopened, synchronize, and ready_for_review.

## 4. app/services/orchestrator.py

**WHAT TO SHOW:** Marker check, changed-file retrieval, diff preparation, prompt build, model call, formatting, and posting.

**WHAT TO SAY:** The orchestrator is the business workflow and keeps each PR event isolated.

**WHY IT MATTERS:** Makes the agent behavior easy to explain.

**POSSIBLE MENTOR QUESTION:** How are duplicates prevented? Answer: comment marker by commit SHA plus delivery tracking.

## 5. app/scm/github_mcp.py

**WHAT TO SHOW:** The three MCP tool calls.

**WHAT TO SAY:** This is the SCM boundary. It knows GitHub tool arguments, while the orchestrator knows only the provider contract.

**WHY IT MATTERS:** Shows clean separation between business workflow and GitHub integration.

**POSSIBLE MENTOR QUESTION:** Is GitHub REST used? Answer: no, not in the final POC.

## 6. app/mcp/github_client.py

**WHAT TO SHOW:** `stdio_client`, `ClientSession`, token environment propagation, `list_tools`, `call_tool`, and cleanup.

**WHAT TO SAY:** The Python service starts and owns the local MCP session. Runtime logs prove connection, discovery, and invocation.

**WHY IT MATTERS:** This is the concrete MCP implementation.

**POSSIBLE MENTOR QUESTION:** What does stdio mean? Answer: the MCP client communicates with a local child process through standard input/output streams.

## 7. app/rules/enterprise_review.md

**WHAT TO SHOW:** Severity definitions, evidence expectations, and governance rules.

**WHAT TO SAY:** Policy is editable Markdown, separate from Python orchestration and model transport.

**WHY IT MATTERS:** Demonstrates controllable enterprise standards.

**POSSIBLE MENTOR QUESTION:** Can the model approve a PR? Answer: no; the policy and formatter keep human approval mandatory.

## 8. app/services/prompt_builder.py

**WHAT TO SHOW:** Policy loading, security boundary, PR metadata, and bounded diff prompt.

**WHAT TO SAY:** Repository content is data, not instructions, and only selected diffs are sent to the model.

**WHY IT MATTERS:** Shows prompt-injection and data-minimization controls.

**POSSIBLE MENTOR QUESTION:** Why not send the whole repository? Answer: cost, privacy, context quality, and attack surface.

## 9. app/llm/client.py

**WHAT TO SHOW:** Generative Engine endpoint call, JSON response request, timeout, and parser.

**WHAT TO SAY:** The model is an OpenAI-compatible inference endpoint; GitHub access remains MCP-owned.

**WHY IT MATTERS:** Clearly separates AI inference from GitHub integration.

**POSSIBLE MENTOR QUESTION:** What happens on malformed output? Answer: validation fails closed and no comment is posted.

## 10. app/models/review.py

**WHAT TO SHOW:** Severity enum, finding fields, line normalization, file counts, and `ReviewResult`.

**WHAT TO SAY:** Pydantic converts model output into a trusted application contract.

**WHY IT MATTERS:** Prevents unstructured model prose from entering the posting path.

**POSSIBLE MENTOR QUESTION:** How are lowercase severities handled? Answer: the finding validator normalizes them before enum validation.

## 11. app/services/review_formatter.py

**WHAT TO SHOW:** Decision, risk, counts, findings, scope, disclaimer, and marker.

**WHAT TO SAY:** The final comment is deterministic and readable for engineers and stakeholders.

**WHY IT MATTERS:** Connects structured output to the visible PR result.

**POSSIBLE MENTOR QUESTION:** How is a review tied to a commit? Answer: the hidden marker includes the commit SHA.

## 12. Terminal Logs

**WHAT TO SHOW:** Uvicorn startup, MCP discovery, tool calls, Generative Engine HTTP 200, and `review_finished result=posted`.

**WHAT TO SAY:** These logs are the operational proof of the end-to-end path.

**WHY IT MATTERS:** Demonstrates actual tool invocation instead of a mocked architecture diagram.

**POSSIBLE MENTOR QUESTION:** Are credentials visible? Answer: no; credentials and authorization headers are never logged.

## 13. GitHub PR

**WHAT TO SHOW:** The generated summary comment and its findings table.

**WHAT TO SAY:** This is the controlled action: one comment, no automatic merge or approval.

**WHY IT MATTERS:** Ends with business-visible value.

**POSSIBLE MENTOR QUESTION:** Can it review multiple repositories? Answer: yes, each webhook carries its repository and the allowlist controls access.

## 14. pytest -q

**WHAT TO SHOW:** Focused tests for security, MCP mocks, orchestration, validation, formatting, and diff bounds.

**WHAT TO SAY:** Tests never require real credentials or external calls.

**WHY IT MATTERS:** Demonstrates repeatable behavior and failure coverage.

## 15. Production Evolution

**WHAT TO SHOW:** README limitations and production evolution section.

**WHAT TO SAY:** The POC proves the flow; production adds durable queues, idempotency, secret management, managed ingress, monitoring, and MCP process supervision.

**WHY IT MATTERS:** Shows architectural maturity without claiming the POC is production infrastructure.
