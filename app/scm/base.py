from abc import ABC, abstractmethod
from dataclasses import dataclass
from app.models.webhook import PullRequestEvent


@dataclass
class ChangedFile:
    path: str
    status: str
    patch: str = ""
    binary: bool = False


class SCMProvider(ABC):
    @abstractmethod
    async def get_pull_request(self, event: PullRequestEvent) -> dict: ...

    @abstractmethod
    async def get_changed_files(self, event: PullRequestEvent) -> list[ChangedFile]: ...

    @abstractmethod
    async def post_review(self, event: PullRequestEvent, body: str) -> None: ...

    @abstractmethod
    async def has_review_marker(self, event: PullRequestEvent, marker: str) -> bool: ...
