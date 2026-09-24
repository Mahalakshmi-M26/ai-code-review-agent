# Security

- Secrets are environment variables only. `.env` is ignored and the application never logs API keys, tokens, webhook secrets, or authorization headers.
- Use a fine-grained GitHub token or GitHub App with only pull request read and issue-comment write access required by the deployment.
- Validate `X-Hub-Signature-256` using HMAC SHA-256 and constant-time comparison before parsing the request.
- Authorize repositories explicitly in production. `ALLOWED_REPOSITORIES=*` is for a controlled demo only.
- Treat PR titles, descriptions, comments, filenames, and source code as untrusted data. Prompt injection defenses are in the policy and prompt builder.
- Send only bounded changed-file diffs to the model. Apply data classification and retention rules before production use.
- Use an organization-approved secret store, workload identity where available, private egress, TLS ingress, rate limits, audit trails, and monitoring in production.
- Pin and scan dependencies, review model/provider terms, and protect logs from sensitive content.
- Add durable idempotency storage and a queue before horizontal scaling. The current in-memory delivery set is intentionally POC-only.
- Human approval remains mandatory. The agent never approves or merges pull requests.
