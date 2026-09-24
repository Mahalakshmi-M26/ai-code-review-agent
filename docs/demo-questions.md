# Mentor Questions and Strong Answers

1. **What is an AI agent?** A bounded system that observes an event, reasons with policy and tools, and performs a controlled action.
2. **Why is this an agent rather than a normal API?** It orchestrates retrieval, policy, model analysis, validation, and GitHub action.
3. **What is MCP?** A standard protocol for exposing tools and context to compatible AI hosts.
4. **Why use MCP?** It gives a governed, reusable tool contract instead of custom tool wiring per assistant.
5. **Which GitHub MCP is used?** GitHub's official `github/github-mcp-server`.
6. **Why not an npm package?** The current official implementation is a Go server with hosted and Docker options.
7. **Where is MCP used here?** VS Code configuration and the provider boundary; the worker keeps an isolated REST fallback.
8. **Why does the worker need a fallback?** A webhook process cannot borrow an interactive VS Code MCP session.
9. **How would Azure DevOps fit?** Implement `SCMProvider` with Azure DevOps MCP calls; orchestration remains unchanged.
10. **What is a webhook?** An authenticated event notification pushed by GitHub.
11. **Why ngrok?** It provides temporary HTTPS ingress to a local PowerShell server.
12. **Is ngrok production ready?** No; use managed ingress, TLS, WAF, rate limiting, and monitoring.
13. **How is the webhook secured?** HMAC SHA-256 with constant-time comparison.
14. **Why verify before parsing?** It prevents untrusted request data from entering application logic.
15. **How are repositories authorized?** `ALLOWED_REPOSITORIES` supports explicit owner/repo values or demo wildcard.
16. **How are multiple PRs isolated?** Each event carries its own immutable context and background task.
17. **How do you scale concurrency?** Move background work to Azure Service Bus, RabbitMQ, Redis Queue, or Kafka.
18. **How are duplicate deliveries handled?** Delivery IDs are deduplicated in memory and commit markers prevent duplicate comments.
19. **What is the production gap?** In-memory state must become durable storage.
20. **How are drafts handled?** Skipped by default and enabled only by configuration.
21. **Which actions are processed?** Opened, reopened, synchronize, and ready_for_review.
22. **How are large PRs handled?** File count, per-file, and total input limits plus ignored/binary-file rules.
23. **Why skip lockfiles?** They often add noise; the limits are configurable.
24. **How is prompt injection addressed?** Repository content is explicitly labeled data, never instructions.
25. **Can the model execute code?** No; the app sends text and does not execute model or repository commands.
26. **How is model output trusted?** It is parsed and validated as `ReviewResult` before posting.
27. **What happens on malformed output?** It raises a controlled error instead of posting unvalidated prose.
28. **Which model is configured?** `MODEL_NAME`, defaulting to the supplied approved-style `openai.gpt-5-mini` identifier.
29. **Where is the API key?** Only in `GEP_API_KEY`, loaded from `.env` or deployment secrets.
30. **Why use an OpenAI-compatible client?** The Generative Engine exposes a compatible chat-completions contract while keeping provider behavior isolated.
31. **What information reaches the model?** Policy, PR metadata, and bounded changed-file diffs only.
32. **What is the review policy?** Markdown under `app/rules/enterprise_review.md`, changeable without Python logic edits.
33. **What severities exist?** BLOCKER, CRITICAL, HIGH, MEDIUM, LOW, and INFO.
34. **Does it auto-approve?** Never; human governance remains required.
35. **How are secrets protected in logs?** Credentials and authorization headers are never logged.
36. **What GitHub permissions are needed?** Least privilege: PR read and comment write for the fallback.
37. **How is reliability addressed?** Timeouts, bounded input, explicit failures, idempotency, and per-event processing.
38. **How is testing performed?** pytest mocks external dependencies and tests security and failure paths.
39. **What observability exists?** Structured stage logs can include correlation, delivery, repository, PR, and SHA context.
40. **What is the next enterprise step?** Durable queue, durable idempotency, secret manager, workload identity, MCP service client, and monitoring.
41. **Why FastAPI?** It offers typed request handling, async support, and a small operational surface.
42. **Why not send the whole repository?** It increases cost, privacy exposure, and prompt-injection surface.
43. **How are dependencies controlled?** Versions are pinned and should be scanned in CI.
44. **What does mock mode prove?** The webhook and orchestration path can be demonstrated without external credentials.
45. **What is the biggest current limitation?** The REST fallback and in-memory state are POC choices, not a production control plane.
