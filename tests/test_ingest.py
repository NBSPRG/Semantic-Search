import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_ingest_stores_text(monkeypatch, client):
    async def fake_insert(text, embedding, metadata):
        assert text == "B2B fintech lead generation"
        assert len(embedding) == 384
        assert metadata == {"source": "test"}
        return 42

    monkeypatch.setattr("app.routes.ingest.vector_store.insert_record", fake_insert)

    response = client.post(
        "/ingest",
        json={"text": "B2B fintech lead generation", "metadata": {"source": "test"}},
    )

    assert response.status_code == 200
    assert response.json() == {"id": 42, "message": "Stored successfully"}


def test_ingest_rejects_empty_text(client):
    response = client.post("/ingest", json={"text": ""})

    assert response.status_code == 422
