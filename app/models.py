from dataclasses import dataclass
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator


@dataclass
class ChangedFile:
    path: str
    status: str
    patch: str = ""
    binary: bool = False


class PullRequestEvent(BaseModel):
    action: str
    delivery_id: str = "unknown"
    repository: str
    owner: str
    pr_number: int = Field(gt=0)
    commit_sha: str
    branch: str
    draft: bool = False
    title: str = ""
    body: str = ""

    @classmethod
    def from_github_payload(cls, payload: dict[str, Any], delivery_id: str) -> "PullRequestEvent":
        repository = payload.get("repository") or {}
        pull_request = payload.get("pull_request") or {}
        base = pull_request.get("base") or {}
        return cls(
            action=payload.get("action", ""),
            delivery_id=delivery_id,
            repository=repository.get("name", ""),
            owner=(repository.get("owner") or {}).get("login", ""),
            pr_number=pull_request.get("number") or payload.get("number"),
            commit_sha=(pull_request.get("head") or {}).get("sha", ""),
            branch=(pull_request.get("head") or {}).get("ref") or base.get("ref", ""),
            draft=bool(pull_request.get("draft", False)),
            title=pull_request.get("title", ""),
            body=pull_request.get("body") or "",
        )

    @property
    def full_name(self) -> str:
        return f"{self.owner}/{self.repository}"


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
        return value.strip().upper() if isinstance(value, str) else value

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
