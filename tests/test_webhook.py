import hashlib
import hmac
import json
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.api import webhook
from app.core.config import Settings


def signed(payload, secret="secret"):
    raw = json.dumps(payload).encode()
    digest = hmac.new(secret.encode(), raw, hashlib.sha256).hexdigest()
    return raw, f"sha256={digest}"


def payload(action="opened", draft=False):
    return {"action": action, "repository": {"name": "repo-a", "owner": {"login": "owner"}}, "pull_request": {"number": 4, "draft": draft, "title": "Test", "head": {"sha": "abc", "ref": "feature"}, "base": {"ref": "main"}}}


def test_webhook_rejects_invalid_and_ignores_irrelevant(monkeypatch):
    app = FastAPI()
    app.include_router(webhook.router)
    settings = Settings(github_webhook_secret="secret", allowed_repositories="owner/repo-a")
    monkeypatch.setattr(webhook, "get_settings", lambda: settings)
    webhook._seen_deliveries.clear()
    client = TestClient(app)
    raw, signature = signed(payload())
    assert client.post("/webhook/github", content=raw, headers={"X-Hub-Signature-256": "sha256=bad", "X-GitHub-Event": "pull_request"}).status_code == 401
    raw, signature = signed(payload("closed"))
    assert client.post("/webhook/github", content=raw, headers={"X-Hub-Signature-256": signature, "X-GitHub-Event": "pull_request"}).json()["status"] == "ignored"


def test_webhook_queues_supported_event_and_skips_draft(monkeypatch):
    app = FastAPI()
    app.include_router(webhook.router)
    settings = Settings(github_webhook_secret="secret", allowed_repositories="owner/repo-a", allow_draft_reviews=False)
    monkeypatch.setattr(webhook, "get_settings", lambda: settings)

    class FakeOrchestrator:
        async def process(self, event):
            return "posted"

    monkeypatch.setattr(webhook, "build_orchestrator", lambda *args: FakeOrchestrator())
    webhook._seen_deliveries.clear()
    client = TestClient(app)
    raw, signature = signed(payload())
    response = client.post("/webhook/github", content=raw, headers={"X-Hub-Signature-256": signature, "X-GitHub-Event": "pull_request", "X-GitHub-Delivery": "delivery-1"})
    assert response.status_code == 202
    assert response.json()["status"] == "queued"
    raw, signature = signed(payload(draft=True))
    response = client.post("/webhook/github", content=raw, headers={"X-Hub-Signature-256": signature, "X-GitHub-Event": "pull_request", "X-GitHub-Delivery": "delivery-2"})
    assert response.json()["reason"] == "draft pull request"


def test_plural_github_webhook_path_is_supported(monkeypatch):
    app = FastAPI()
    app.include_router(webhook.router)
    settings = Settings(github_webhook_secret="secret", allowed_repositories="owner/repo-a")
    monkeypatch.setattr(webhook, "get_settings", lambda: settings)
    monkeypatch.setattr(webhook, "build_orchestrator", lambda *args: type("FakeOrchestrator", (), {"process": lambda self, event: None})())
    webhook._seen_deliveries.clear()
    client = TestClient(app)
    raw, signature = signed(payload())
    response = client.post("/webhooks/github", content=raw, headers={"X-Hub-Signature-256": signature, "X-GitHub-Event": "pull_request", "X-GitHub-Delivery": "plural-path"})
    assert response.status_code == 202
    assert response.json()["status"] == "queued"
