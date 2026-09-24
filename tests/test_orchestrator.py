import asyncio
from app.core.config import Settings
from app.models.review import ReviewResult
from app.models.webhook import PullRequestEvent
from app.scm.base import ChangedFile
from app.services.orchestrator import ReviewOrchestrator


class FakeSCM:
    def __init__(self):
        self.posted = []
        self.duplicate = False

    async def has_review_marker(self, event, marker):
        return self.duplicate

    async def get_changed_files(self, event):
        return [ChangedFile("app.py", "modified", "print('x')")]

    async def post_review(self, event, body):
        self.posted.append(body)


class FakeLLM:
    async def review(self, prompt):
        return ReviewResult(summary="ok", categories_reviewed=["Security"])


def test_orchestrator_posts_once_and_is_idempotent(tmp_path):
    policy = tmp_path / "policy.md"
    policy.write_text("policy", encoding="utf-8")
    settings = Settings(max_files=5, policy_path=policy) if False else Settings(max_files=5)
    scm, llm = FakeSCM(), FakeLLM()
    result = ReviewOrchestrator(settings, scm, llm)
    event = PullRequestEvent(action="opened", repository="repo", owner="owner", pr_number=1, commit_sha="sha", branch="main")
    assert asyncio.run(result.process(event)) == "posted"
    assert len(scm.posted) == 1
    scm.duplicate = True
    assert asyncio.run(result.process(event)) == "duplicate"
