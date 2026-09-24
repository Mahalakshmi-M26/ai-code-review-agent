# Security

## Webhook Authentication

The webhook handler verifies `X-Hub-Signature-256` with HMAC-SHA256 and constant-time comparison before parsing the payload. Unsupported events, malformed payloads, unauthorized repositories, and disallowed draft PRs are rejected or ignored.

## Secret Management

Secrets are loaded from environment variables through `pydantic-settings`. `.env` is ignored by Git. The application does not log API keys, GitHub tokens, webhook secrets, or authorization headers. Production should use an approved secret manager and workload identity where available.

## MCP Authentication

`GITHUB_MCP_TOKEN` is passed only to the local MCP subprocess as `GITHUB_PERSONAL_ACCESS_TOKEN`. Use a least-privilege GitHub credential with the read and issue-comment permissions needed by the configured MCP tools.

## Repository Authorization

`ALLOWED_REPOSITORIES` accepts comma-separated repository values. Matching is case-insensitive and supports `owner/repository` values or repository names.

`ALLOWED_REPOSITORIES=*` is convenient for a controlled local POC where the webhook endpoint and test repositories are known. It permits every repository and must not be used as the production authorization policy. Production should use an explicit allowlist or an identity-based authorization service.

## Prompt Injection Protection

PR titles, descriptions, comments, filenames, source code, and diffs are untrusted data. The prompt builder labels them as data and instructs the model to ignore instructions embedded in repository content. The application never executes repository code or model-generated commands.

## Input and Output Controls

Changed files are bounded by count, per-file diff length, and total review input. Generated, lock, ignored, and binary files are skipped. Model JSON is parsed and validated as `ReviewResult` and `ReviewFinding` before formatting or posting.

## Logging Security

Logs contain operational stage information such as repository, PR number, commit SHA, tool name, and result. They must not contain credentials, authorization headers, or full source diffs.

## Human Governance

The agent posts comments only. It does not approve, merge, deploy, or change repository code. Humans remain responsible for decisions and remediation.

## Production Evolution

Replace ngrok with managed ingress, background tasks with a durable queue, in-memory delivery tracking with durable idempotency, local secrets with a secret manager, and local process supervision with an approved managed MCP runtime. Add rate limits, audit trails, monitoring, dependency scanning, and controlled egress.
