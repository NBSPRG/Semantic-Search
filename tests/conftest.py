import pytest

from app.services.embedder import get_embedder


class FakeEmbedder:
    is_loaded = True

    async def encode(self, text: str) -> list[float]:
        seed = sum(ord(char) for char in text) % 100
        return [float(seed) / 100.0] * 384


@pytest.fixture(autouse=True)
def fake_runtime(monkeypatch):
    async def noop():
        return None

    async def ping():
        return True

    monkeypatch.setattr("app.routes.ingest.get_embedder", lambda: FakeEmbedder())
    monkeypatch.setattr("app.routes.search.get_embedder", lambda: FakeEmbedder())
    monkeypatch.setattr("app.main.get_embedder", lambda: FakeEmbedder())
    monkeypatch.setattr("app.main.database.connect", noop)
    monkeypatch.setattr("app.main.database.close", noop)
    monkeypatch.setattr("app.main.database.ping", ping)
    get_embedder.cache_clear()
