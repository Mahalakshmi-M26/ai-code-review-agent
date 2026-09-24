from app.models.review import ReviewFinding, ReviewResult, Severity
from app.services.review_formatter import format_review


def test_formatter_includes_severity_and_marker():
    result = ReviewResult(decision="CHANGES REQUIRED", risk_level="High", findings=[ReviewFinding(severity=Severity.HIGH, category="Security", file="app.py", line=4, title="Unsafe input", issue="Input is not validated.", impact="Unexpected data can reach a sensitive operation.", recommendation="Validate at the boundary.", suggested_fix="Use a typed request model.")])
    output = format_review(result, "<!-- ai-code-review-agent:abc -->")
    assert "[HIGH] Security - Unsafe input" in output
    assert "| High | 1 |" in output
    assert "<!-- ai-code-review-agent:abc -->" in output
