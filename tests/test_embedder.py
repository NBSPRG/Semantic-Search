import pytest

from app.services.embedder import Embedder


class TinyModel:
    def encode(self, text, normalize_embeddings=True, convert_to_numpy=True):
        assert text == "hello"
        assert normalize_embeddings is True
        assert convert_to_numpy is True
        return [0.1, 0.2, 0.3]


@pytest.mark.asyncio
async def test_embedder_returns_float_list(monkeypatch):
    monkeypatch.setattr("app.services.embedder.SentenceTransformer", lambda _: TinyModel())

    embedder = Embedder("tiny-model")
    embedding = await embedder.encode("hello")

    assert embedding == pytest.approx([0.1, 0.2, 0.3])
    assert embedder.is_loaded is True
