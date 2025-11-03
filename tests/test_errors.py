from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_problem_details_has_correlation_id_on_404():
    r = client.get("/non-existent-path")
    assert r.status_code == 404
    body = r.json()
    assert body["status"] == 404
    assert body["title"] == "Not Found"
    assert "correlation_id" in body

