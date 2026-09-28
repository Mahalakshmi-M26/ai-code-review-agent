import asyncio
from app.config import Settings
from app.models import ChangedFile, PullRequestEvent, ReviewResult
from app.reviewer import ReviewOrchestrator


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


def test_orchestrator_keeps_only_lines_added_in_diff():
    class DiffSCM(FakeSCM):
        async def get_changed_files(self, event):
            patch = "\n".join([
                "@@ -75,2 +79,3 @@",
                " context()",
                "-old_call()",
                "+new_call()",
                "@@ -100,1 +102,0 @@",
                "-removed_only()",
            ])
            return [ChangedFile("app.py", "modified", patch)]

    class FindingsLLM:
        async def review(self, prompt):
            return ReviewResult(findings=[
                {"severity": "MEDIUM", "category": "Reliability", "file": "app.py", "line": 80, "title": "Changed code", "issue": "Issue", "recommendation": "Fix", "suggested_fix": None},
                {"severity": "LOW", "category": "Reliability", "file": "app.py", "line": 102, "title": "Deleted code", "issue": "Issue", "recommendation": "Fix", "suggested_fix": None},
            ])

    scm = DiffSCM()
    settings = Settings()
    event = PullRequestEvent(action="opened", repository="repo", owner="owner", pr_number=1, commit_sha="sha", branch="main")
    asyncio.run(ReviewOrchestrator(settings, scm, FindingsLLM()).process(event))

    assert "📍 Line 80" in scm.posted[0]
    assert "📍 Line unavailable" in scm.posted[0]
