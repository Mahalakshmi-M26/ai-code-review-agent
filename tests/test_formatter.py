from app.models import ReviewFinding, ReviewResult, Severity
from app.reviewer import format_review


def test_formatter_includes_severity_and_marker():
    result = ReviewResult(
        risk_level="Medium",
        summary="Input validation is missing at the request boundary.",
        merge_recommendation="Do not merge until the request input is validated.",
        findings=[ReviewFinding(
            severity=Severity.MEDIUM,
            category="Coding Standards",
            file="app.py",
            line=79,
            title="Validate request input",
            issue="The request value is used without validation.",
            recommendation="Validate the value before using it.",
            suggested_fix="validated_value = RequestModel.model_validate(raw_value)",
        )],
    )
    output = format_review(result, "<!-- ai-code-review-agent:abc -->")
    assert output.index("## Overall Assessment") < output.index("## Review Summary") < output.index("### 🟡 MEDIUM | Coding Standards")
    assert "## Overall Assessment: 🟡 MODERATE RISK" in output
    assert "- 🟡 **Medium:** 1" in output
    assert "📁 `app.py` | 📍 Line 79" in output
    assert "**Issue**\n\nThe request value is used without validation." in output
    assert "**Recommendation**\n\nValidate the value before using it." in output
    assert "```\nvalidated_value = RequestModel.model_validate(raw_value)\n```" in output
    assert "**Impact**" not in output
    assert "## Merge Recommendation\n\nDo not merge until the request input is validated." in output
    assert "<!-- ai-code-review-agent:abc -->" in output
