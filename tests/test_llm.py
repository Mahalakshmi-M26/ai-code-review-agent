import pytest
from app.llm.client import LLMClient


def test_malformed_model_response_is_rejected():
    with pytest.raises(ValueError):
        LLMClient.parse_result("not json")


def test_structured_model_response_is_validated():
    result = LLMClient.parse_result('{"decision":"NO BLOCKING ISSUES","risk_level":"Low","findings":[],"summary":"ok"}')
    assert result.decision == "NO BLOCKING ISSUES"


def test_model_review_shape_is_normalized_before_formatting():
    result = LLMClient.parse_result(
        '{"decision":"CHANGES REQUIRED","risk_level":"High",'
        '"findings":[{"severity":"HIGH","category":"Security",'
        '"file":"app.py","line":"diff hunk starting at line 5",'
        '"title":"Unsafe input","issue":"Input is not validated.",'
        '"impact":"Invalid data can reach the operation.",'
        '"recommendation":"Validate at the boundary.",'
        '"suggested_fix":"Use a typed request model."}],'
        '"summary":"Review completed","files_reviewed":["app.py"],'
        '"files_skipped":[],"categories_reviewed":["Security"]}'
    )
    assert result.findings[0].line is None
    assert result.files_reviewed == 1
    assert result.files_skipped == 0


def test_model_severity_is_case_insensitive():
    result = LLMClient.parse_result(
        '{"findings":[{"severity":"low","category":"Testing",'
        '"title":"Minor issue","issue":"Issue","impact":"Impact",'
        '"recommendation":"Fix it","suggested_fix":"Apply the fix"}]}'
    )
    assert result.findings[0].severity.value == "LOW"
