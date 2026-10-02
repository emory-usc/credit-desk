"""CI smoke test for the Credit Desk API surface."""

from fastapi.testclient import TestClient

from underwriting_agent.server import app

c = TestClient(app)
assert c.get("/health").status_code == 200
assert c.get("/ready").status_code == 200
r = c.post(
    "/underwrite",
    json={"applicant_id": "app-001"},
    headers={"X-API-Key": "dev-key"},
)
assert r.status_code == 200
assert r.json()["decision"] == "approve"
print("API smoke OK")
