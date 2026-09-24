# Mentor Questions and Strong Answers

1. **What is an AI agent?** A system that observes an event, uses policy and tools to reason about it, and performs a bounded action.
2. **Why is this an agent?** It combines event handling, retrieval, policy, model analysis, validation, and a controlled GitHub action.
3. **What is MCP?** A standard protocol for exposing tools and context to an AI-capable client.
4. **Where exactly is MCP used?** `GitHubMCPClient` owns the MCP session and `GitHubMCPProvider` invokes GitHub tools.
5. **How do you prove MCP is used?** Startup logs show tool discovery and runtime logs show each MCP tool call and success.
6. **What is stdio?** Communication with a local child process through standard input and output streams.
7. **Why local MCP?** The webhook worker needs its own unattended tool session rather than an interactive host session.
8. **Why not direct GitHub REST?** MCP provides a governed tool contract and one explicit GitHub integration boundary.
9. **Are you using REST anywhere for GitHub?** No. GitHub operations are MCP-only; the Generative Engine uses HTTP separately.
10. **How does the webhook work?** GitHub sends a signed pull-request event to the ngrok URL, and FastAPI validates and routes it.
11. **What does ngrok do?** It gives GitHub a temporary HTTPS route to the local FastAPI process.
12. **Why is ngrok not production infrastructure?** It is a developer tunnel, not managed ingress, WAF, durable routing, or enterprise observability.
13. **What does the orchestrator do?** It coordinates idempotency, MCP retrieval, diff preparation, prompting, inference, validation, formatting, and posting.
14. **What does the Generative Engine do?** It analyzes policy plus bounded PR context and returns structured review JSON.
15. **Why use Markdown review rules?** Policy can be reviewed and changed by stakeholders without changing Python control flow.
16. **Why Pydantic?** It validates the model response against a typed contract before any comment is posted.
17. **How do you handle hallucinated output?** Invalid structure, missing fields, invalid severities, or malformed JSON fail closed.
18. **How do you prevent prompt injection?** Repository content is labeled untrusted data and the prompt explicitly rejects embedded instructions.
19. **How are secrets protected?** They come from environment configuration, `.env` is ignored, and credentials are excluded from logs.
20. **How do multiple repositories work?** The event carries owner and repository, and MCP arguments are built per event.
21. **What does `ALLOWED_REPOSITORIES=*` mean?** Every repository is accepted; it is convenient for a controlled POC but broad.
22. **How would production authorization differ?** Use an explicit allowlist, GitHub App identity, or an authorization service.
23. **How are duplicate reviews prevented?** The orchestrator searches for a commit marker and the webhook tracks delivery IDs in memory.
24. **Can concurrent PRs be processed?** FastAPI background tasks isolate event context, but production needs a durable worker queue.
25. **What happens if MCP fails?** Startup or the review task fails explicitly; the app does not silently use a second GitHub integration.
26. **What happens if the LLM fails?** The task logs the failure and no unvalidated review is posted.
27. **How would this scale?** Move background work to a durable queue, add durable idempotency, and run managed workers.
28. **How would Azure DevOps be added?** Implement the same SCM provider contract with Azure DevOps MCP operations.
29. **Would you allow AI to merge PRs?** No. This POC only posts comments and keeps human governance mandatory.
30. **How would this be monitored?** Add metrics, traces, audit logs, queue health, MCP process health, model latency, and failure alerts.
31. **Which MCP tools are required?** `get_pull_request_comments`, `get_pull_request_files`, and `add_issue_comment`.
32. **What happens if a required tool is missing?** Startup raises an MCP connection error and the service does not proceed.
33. **Why check comments before files?** It avoids model and posting work when the commit was already reviewed.
34. **What data reaches the model?** Policy, PR metadata, and selected bounded changed-file diffs.
35. **Why skip lockfiles and generated files?** They add noise and consume context without improving most review decisions.
36. **What are the size controls?** Maximum file count, per-file diff characters, and total review input characters.
37. **Which webhook actions are reviewed?** `opened`, `reopened`, `synchronize`, and `ready_for_review`.
38. **Are draft PRs reviewed?** Not by default; `ALLOW_DRAFT_REVIEWS` controls that behavior.
39. **What does the health endpoint prove?** That the FastAPI service is responding; MCP startup logs prove the integration is ready.
40. **What is the review output?** Decision, risk level, severity counts, findings, categories, scope, remediation, disclaimer, and marker.
41. **What happens when severity is lowercase?** The Pydantic validator normalizes it before enum validation.
42. **Why not send model-generated code directly to GitHub?** The agent posts a review comment only; it does not modify source code.
43. **How is human approval preserved?** The policy, formatter, and action boundary explicitly avoid approval and merge operations.
44. **What is the biggest POC limitation?** Delivery tracking, idempotency, and background execution are in memory.
45. **What replaces in-memory state in production?** A durable idempotency store and queue-backed workflow.
46. **Why is the MCP token passed as an environment variable?** The local server expects `GITHUB_PERSONAL_ACCESS_TOKEN`, and this avoids embedding it in command arguments.
47. **Can the MCP command be changed?** Yes, through `GITHUB_MCP_COMMAND` and `GITHUB_MCP_ARGS`, subject to enterprise approval.
48. **Why is the Generative Engine not MCP?** It is the inference service and is called through its OpenAI-compatible HTTP API; MCP governs GitHub tools.
49. **How is the repository allowlist matched?** Case-insensitive full name or repository-name matching, with `*` wildcard support.
50. **What would production ingress look like?** Managed HTTPS ingress with authentication, rate limiting, WAF controls, and observability.
