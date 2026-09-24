from enum import Enum
from pydantic import BaseModel, Field, field_validator


class Severity(str, Enum):
    BLOCKER = "BLOCKER"
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class ReviewFinding(BaseModel):
    severity: Severity
    category: str
    file: str = ""
    line: int | None = None
    title: str
    issue: str
    impact: str
    recommendation: str
    suggested_fix: str

    @field_validator("severity", mode="before")
    @classmethod
    def normalize_severity(cls, value):
        if isinstance(value, str):
            return value.strip().upper()
        return value

    @field_validator("line", mode="before")
    @classmethod
    def normalize_line_reference(cls, value):
        if value is None or isinstance(value, int):
            return value
        if isinstance(value, str):
            try:
                return int(value.strip())
            except ValueError:
                return None
        return None


class ReviewResult(BaseModel):
    decision: str = "NO BLOCKING ISSUES"
    risk_level: str = "Low"
    findings: list[ReviewFinding] = Field(default_factory=list)
    summary: str = ""
    files_reviewed: int = 0
    files_skipped: int = 0
    categories_reviewed: list[str] = Field(default_factory=list)

    @field_validator("files_reviewed", "files_skipped", mode="before")
    @classmethod
    def normalize_file_count(cls, value):
        if isinstance(value, (list, tuple, set)):
            return len(value)
        if isinstance(value, str):
            try:
                return int(value.strip())
            except ValueError:
                return 0
        return value

    def counts(self) -> dict[str, int]:
        return {severity.value: sum(f.severity == severity for f in self.findings) for severity in Severity}
