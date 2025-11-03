from fastapi.testclient import TestClient

from app.main import app


def test_login_rate_limiting_applies():
    client = TestClient(app)
    # Hit the login endpoint more than allowed without registering to force failures
    for _ in range(5):
        client.post("/auth/login", json={"email": "x@example.com", "password": "bad"})
    r = client.post("/auth/login", json={"email": "x@example.com", "password": "bad"})
    assert r.status_code == 429
    body = r.json()
    assert body["status"] == 429
    assert body["title"] == "Too Many Requests"

