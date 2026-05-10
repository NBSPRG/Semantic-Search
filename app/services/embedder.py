import asyncio
from functools import lru_cache

import numpy as np
from sentence_transformers import SentenceTransformer

from app.core.config import get_settings


class Embedder:
    def __init__(self, model_name: str) -> None:
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)

    def encode_sync(self, text: str) -> list[float]:
        embedding = self.model.encode(
            text,
            normalize_embeddings=True,
            convert_to_numpy=True,
        )
        return np.asarray(embedding, dtype=np.float32).tolist()

    async def encode(self, text: str) -> list[float]:
        timeout = get_settings().embedding_timeout_seconds
        return await asyncio.wait_for(asyncio.to_thread(self.encode_sync, text), timeout=timeout)

    @property
    def is_loaded(self) -> bool:
        return self.model is not None


@lru_cache
def get_embedder() -> Embedder:
    return Embedder(get_settings().model_name)
