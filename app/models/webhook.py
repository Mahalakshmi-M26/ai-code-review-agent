from typing import Any
from pydantic import BaseModel, Field


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
