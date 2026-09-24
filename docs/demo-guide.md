# 10-15 Minute Demo

1. **Problem, 1 minute:** Code reviews should reserve human attention for design and business risk.
2. **Architecture, 2 minutes:** Show `README.md` diagram and `docs/architecture.md` sequence.
3. **Agent behavior, 1 minute:** Explain webhook trigger, policy, bounded context, model reasoning, validation, and action.
4. **MCP, 1 minute:** Open `docs/mcp-integration.md` and `.vscode/mcp.json`; show the official hosted server and isolated REST fallback.
5. **Security, 1 minute:** Open `app/core/security.py`, `app/core/config.py`, and `docs/security.md`.
6. **Live flow, 4 minutes:** Show `.env` with secrets hidden, start Uvicorn, start `ngrok http 8000`, create a test PR containing a deliberately unsafe change, and show the GitHub delivery plus structured comment.
7. **Tests, 2 minutes:** Run `pytest -q` and point to signature, draft, multi-repo, malformed-response, diff-limit, and idempotency tests.
8. **Future, 1 minute:** Explain durable queue/idempotency, service-side MCP client, Azure DevOps provider, and secret store.

Recommended VS Code order: `README.md`, `.vscode/mcp.json`, `app/api/webhook.py`, `app/services/orchestrator.py`, `app/rules/enterprise_review.md`, `app/llm/client.py`, `app/scm/github_mcp.py`, `docs/security.md`, then `tests/`.

Do not show credential values. Keep `MOCK_EXTERNAL_SERVICES=true` for a safe dry run, or switch it off only after credentials and network access are verified.
