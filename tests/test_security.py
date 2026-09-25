import hashlib
import hmac
from app.security import verify_github_signature


def test_signature_validation():
    payload, secret = b'{"ok":true}', "secret"
    digest = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    assert verify_github_signature(payload, f"sha256={digest}", secret)
    assert not verify_github_signature(payload, "sha256=bad", secret)
    assert not verify_github_signature(payload, None, secret)
