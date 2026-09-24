# Troubleshooting

## MCP Server Fails to Start

Confirm Node.js and `npx` are installed and available in the same PowerShell environment that starts Uvicorn. Verify `GITHUB_MCP_COMMAND`, `GITHUB_MCP_ARGS`, and `GITHUB_MCP_TOKEN` without printing the token. Try the command independently only if your security policy permits it.

## MCP Connection Fails

Check the FastAPI startup logs. The application must log `github_mcp_connected` before it accepts reviews. A missing token, failed subprocess, or initialization error stops startup.

## Required MCP Tool Unavailable

Compare the discovered tools with `GITHUB_MCP_TOOLS`. The final POC requires `get_pull_request_comments`, `get_pull_request_files`, and `add_issue_comment`. Correct the local MCP server configuration rather than bypassing MCP.

## GitHub Authentication Failure

Confirm the token is valid, unexpired, available to the local MCP process, and has the least-privilege repository permissions required for reading PR data and creating issue comments. Rotate exposed credentials immediately.

## Webhook Not Received

Check that Uvicorn is running on port 8000, ngrok forwards to port 8000, the GitHub webhook URL ends in `/webhooks/github`, and the selected event is `Pull requests`. Inspect the GitHub delivery result and the ngrok terminal.

## Webhook Signature Invalid

Ensure the GitHub webhook secret exactly matches `GITHUB_WEBHOOK_SECRET`. Do not transform the body before signature verification. Confirm the request includes `X-Hub-Signature-256`.

## ngrok URL Changed

Restarting or changing the ngrok tunnel may change its public HTTPS URL. Update the GitHub webhook URL whenever the forwarding URL changes.

## Generative Engine Failure

Check `OPENAI_BASE_URL`, `GEP_API_KEY`, `MODEL_NAME`, network access, and the configured timeout. Set `MOCK_EXTERNAL_SERVICES=true` to validate the local application path without a model call.

## Malformed LLM Output

The client accepts JSON, including JSON fenced in a code block, and rejects invalid responses. Check the model response contract and prompt. The review is not posted when parsing fails.

## Pydantic Validation Failure

Inspect the required fields in `ReviewResult` and `ReviewFinding`: decision, risk level, findings, summary, file counts, categories, and finding evidence. Invalid severity or missing required finding fields causes a controlled failure.

## Duplicate Review Intentionally Skipped

The orchestrator checks for `<!-- ai-code-review-agent:<commit-sha> -->`. The webhook handler also tracks delivery IDs in memory. A duplicate delivery or an already-reviewed commit returns without posting another comment.

## Repository Not Authorized

Set `ALLOWED_REPOSITORIES` to `*` only for a controlled POC, or add the exact `owner/repository` value for a restricted demo. Check capitalization and the repository name in the webhook payload.
