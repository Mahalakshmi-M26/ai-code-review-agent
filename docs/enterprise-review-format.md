# Enterprise Review Format

The formatter creates one summary comment containing:

- Review decision.
- Risk level.
- Counts for BLOCKER, CRITICAL, HIGH, MEDIUM, LOW, and INFO findings.
- Detailed findings with category, file, line, title, issue, impact, recommendation, and suggested remediation.
- Categories reviewed.
- Files reviewed and skipped.
- AI-generated disclaimer.
- Hidden commit marker for idempotency.

The model response is parsed as JSON and validated by Pydantic before the formatter runs. Malformed or incomplete output is rejected and is never posted as an unstructured comment.
