"""Tests for the FastAPI delivery surface."""

from fastapi.testclient import TestClient

from underwriting_agent.server import app

client = TestClient(app)


def test_health_is_unauthenticated():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_ready_reports_applicant_book():
    r = client.get("/ready")
    assert r.status_code == 200
    assert r.json()["applicants"] == 10


def test_underwrite_with_valid_key():
    r = client.post(
        "/underwrite",
        json={"applicant_id": "app-001"},
        headers={"X-API-Key": "dev-key"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["decision"] == "approve"
    assert body["advisory"] is True


def test_underwrite_rejects_missing_key():
    r = client.post("/underwrite", json={"applicant_id": "app-001"})
    assert r.status_code == 401


def test_underwrite_rejects_wrong_key():
    r = client.post(
        "/underwrite",
        json={"applicant_id": "app-001"},
        headers={"X-API-Key": "wrong"},
    )
    assert r.status_code == 401


def test_underwrite_unknown_applicant_is_404():
    r = client.post(
        "/underwrite",
        json={"applicant_id": "nope"},
        headers={"X-API-Key": "dev-key"},
    )
    assert r.status_code == 404
