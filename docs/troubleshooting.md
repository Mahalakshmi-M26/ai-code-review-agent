# Troubleshooting

**404 on webhook delivery:** Use `<ngrok-url>/webhooks/github`. The service also accepts the legacy singular `/webhook/github` path.

**401 Invalid webhook signature:** Ensure GitHub's secret exactly matches `GITHUB_WEBHOOK_SECRET`, the payload is sent as JSON, and the endpoint receives `X-Hub-Signature-256`.

**403 Repository is not authorized:** Add the exact `owner/repo` to `ALLOWED_REPOSITORIES`, or use `*` only for a controlled demo.

**No comment appears:** Check the PowerShell logs, GitHub delivery redelivery page, draft status, action, duplicate commit marker, token permissions, and ngrok forwarding URL.

**Model call fails:** Confirm `OPENAI_BASE_URL`, `GEP_API_KEY`, and an approved `MODEL_NAME`. Temporarily set `MOCK_EXTERNAL_SERVICES=true` to validate the application path.

**MCP does not start:** For the local setup, confirm `GITHUB_MCP_TRANSPORT=stdio`, `GITHUB_MCP_COMMAND=npx`, `GITHUB_MCP_ARGS=-y @modelcontextprotocol/server-github`, and that `GITHUB_MCP_TOKEN` is configured. A PowerShell process variable overrides `.env`; clear it with `Remove-Item Env:GITHUB_MCP_TRANSPORT -ErrorAction SilentlyContinue` before restarting.

**Application still reports `SCM_PROVIDER=github`:** A PowerShell process environment variable overrides `.env`. Run `Remove-Item Env:SCM_PROVIDER -ErrorAction SilentlyContinue`, open a fresh terminal, and start the application again.

**Hosted MCP redirects to `web-notification.capgemini.com`:** This is a corporate network redirect, not a GitHub MCP response. Use the local stdio configuration above, or check the corporate proxy, VPN, firewall, or organization-approved egress policy before using hosted HTTP again.

**Large PR:** Adjust `MAX_FILES`, `MAX_FILE_DIFF_CHARS`, and `MAX_REVIEW_INPUT_CHARS`; generated, binary, and lock files are intentionally skipped.

**PowerShell activation blocked:** Run `Set-ExecutionPolicy -Scope Process Bypass` in the current PowerShell session, then activate `.venv`.
