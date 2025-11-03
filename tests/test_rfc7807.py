from fastapi.testclient import TestClient

from app.main import app


def test_validation_problem_details_on_register():
    client = TestClient(app)
    # invalid email and too short password
    r = client.post("/auth/register", json={"email": "invalid-email", "password": "123"})
    assert r.status_code == 422
    body = r.json()
    assert body["status"] == 422
    assert body["title"] == "Input validation error"
    assert "errors" in body


def test_http_exception_problem_details_on_duplicate_email():
    client = TestClient(app)
    client.post("/auth/register", json={"email": "dup@example.com", "password": "password123"})
    r = client.post("/auth/register", json={"email": "dup@example.com", "password": "password123"})
    assert r.status_code == 400
    body = r.json()
    assert body["status"] == 400
    assert body["title"] == "Bad Request"
    assert "correlation_id" in body

