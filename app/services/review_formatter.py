from app.models.review import ReviewResult, Severity


def format_review(result: ReviewResult, marker: str) -> str:
    counts = result.counts()
    lines = ["## AI Code Review Summary", "", f"### Review Decision\n{result.decision}", f"\n### Risk Level\n{result.risk_level}", "\n### Findings", "", "| Severity | Count |", "|---|---:|"]
    lines.extend(f"| {severity.value.title()} | {counts[severity.value]} |" for severity in Severity)
    lines += ["", "### Detailed Findings"]
    for finding in result.findings:
        location = f"{finding.file}:{finding.line}" if finding.line else finding.file or "PR scope"
        lines += [f"\n#### [{finding.severity.value}] {finding.category} - {finding.title}", f"**File:** `{location}`", f"**Issue:** {finding.issue}", f"**Impact:** {finding.impact}", f"**Recommendation:** {finding.recommendation}", f"**Suggested remediation:** {finding.suggested_fix}"]
    lines += ["", "### Categories Reviewed", ", ".join(result.categories_reviewed) or "Security, Architecture, Testing, Maintainability", f"\n**Scope:** Files reviewed: {result.files_reviewed}; files skipped: {result.files_skipped}", "", "> AI-generated review. Human approval remains required according to the team's governance process.", "", marker]
    return "\n".join(lines)
