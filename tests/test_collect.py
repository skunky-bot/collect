from fastapi.testclient import TestClient
from app import app

client = TestClient(app)


def test_normalize_requires_auth_and_does_not_enable_outreach(monkeypatch):
    monkeypatch.setenv("SKUNKY_SERVICE_TOKEN", "test-only")
    data = {
        "source_id": "fixture", "source_url": "https://example.com/",
        "emails": ["INFO@Example.COM", "info@example.com", "not-email"],
        "phones": ["082 123 4567", "0821234567"]
    }
    assert client.post("/v1/normalize", json=data).status_code == 401
    response = client.post("/v1/normalize", json=data, headers={"X-Skunky-Token": "test-only"})
    assert response.status_code == 200
    body = response.json()
    assert body["emails"] == ["info@example.com"]
    assert body["phones"] == ["+27821234567"]
    assert body["outreach_allowed"] is False
    assert body["persisted"] is False
