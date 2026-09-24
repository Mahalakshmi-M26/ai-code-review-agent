# Enterprise Review Format

The formatter posts:

- Decision: `CHANGES REQUIRED`, `APPROVED WITH COMMENTS`, or `NO BLOCKING ISSUES`.
- Risk level: Critical, High, Medium, or Low.
- Severity table: BLOCKER, CRITICAL, HIGH, MEDIUM, LOW, INFO counts.
- Detailed findings with category, file, line, issue, impact, recommendation, and suggested remediation.
- Categories reviewed and scope counts.
- AI-generated disclaimer and a hidden commit marker.

The model must return JSON validated by Pydantic before formatting. Malformed responses fail closed instead of being posted as casual prose.
