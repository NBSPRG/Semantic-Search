import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_search_returns_ranked_results(monkeypatch, client):
    async def fake_search(embedding, top_k):
        assert len(embedding) == 384
        assert top_k == 3
        return [
            {
                "id": 42,
                "text": "Looking for B2B SaaS leads in fintech",
                "similarity": 0.94,
                "metadata": {"source": "form"},
            }
        ]

    monkeypatch.setattr("app.routes.search.vector_store.search", fake_search)

    response = client.post("/search", json={"query": "fintech SaaS companies", "top_k": 3})

    assert response.status_code == 200
    assert response.json() == {
        "results": [
            {
                "id": 42,
                "text": "Looking for B2B SaaS leads in fintech",
                "similarity": 0.94,
                "metadata": {"source": "form"},
            }
        ]
    }


def test_search_rejects_invalid_top_k(client):
    response = client.post("/search", json={"query": "fintech", "top_k": 0})

    assert response.status_code == 422
