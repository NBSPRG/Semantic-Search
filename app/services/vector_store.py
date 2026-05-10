import json
import math
from dataclasses import dataclass, field
from threading import Lock
from typing import Any

from app.core.config import get_settings
from app.db.connection import database


def _to_pgvector(embedding: list[float]) -> str:
    return "[" + ",".join(f"{value:.8f}" for value in embedding) + "]"


def _metadata_to_dict(metadata: Any) -> dict[str, Any]:
    if metadata is None:
        return {}
    if isinstance(metadata, str):
        return json.loads(metadata)
    return dict(metadata)


class PostgresVectorStore:
    async def insert_record(
        self,
        text: str,
        embedding: list[float],
        metadata: dict[str, Any] | None = None,
    ) -> int:
        if not embedding:
            raise ValueError("Embedding cannot be empty.")

        async with database.acquire() as connection:
            record_id = await connection.fetchval(
                """
                INSERT INTO records (input_text, embedding, metadata)
                VALUES ($1, $2::vector, $3::jsonb)
                RETURNING id
                """,
                text,
                _to_pgvector(embedding),
                json.dumps(metadata or {}),
            )
        return int(record_id)

    async def search(self, embedding: list[float], top_k: int) -> list[dict[str, Any]]:
        async with database.acquire() as connection:
            rows = await connection.fetch(
                """
                SELECT
                    id,
                    input_text,
                    1 - (embedding <=> $1::vector) AS similarity,
                    metadata
                FROM records
                ORDER BY embedding <=> $1::vector
                LIMIT $2
                """,
                _to_pgvector(embedding),
                top_k,
            )

        return [
            {
                "id": row["id"],
                "text": row["input_text"],
                "similarity": float(row["similarity"]),
                "metadata": _metadata_to_dict(row["metadata"]),
            }
            for row in rows
        ]


@dataclass
class StoredRecord:
    id: int
    text: str
    embedding: list[float]
    metadata: dict[str, Any] = field(default_factory=dict)


class MemoryVectorStore:
    def __init__(self) -> None:
        self._records: list[StoredRecord] = []
        self._next_id = 1
        self._lock = Lock()

    async def insert_record(
        self,
        text: str,
        embedding: list[float],
        metadata: dict[str, Any] | None = None,
    ) -> int:
        if not embedding:
            raise ValueError("Embedding cannot be empty.")

        with self._lock:
            record_id = self._next_id
            self._next_id += 1
            self._records.append(
                StoredRecord(
                    id=record_id,
                    text=text,
                    embedding=embedding,
                    metadata=metadata or {},
                )
            )
        return record_id

    async def search(self, embedding: list[float], top_k: int) -> list[dict[str, Any]]:
        with self._lock:
            records = list(self._records)

        ranked = sorted(
            records,
            key=lambda record: _cosine_similarity(embedding, record.embedding),
            reverse=True,
        )[:top_k]

        return [
            {
                "id": record.id,
                "text": record.text,
                "similarity": _cosine_similarity(embedding, record.embedding),
                "metadata": record.metadata,
            }
            for record in ranked
        ]


def _cosine_similarity(left: list[float], right: list[float]) -> float:
    dot = sum(a * b for a, b in zip(left, right))
    left_norm = math.sqrt(sum(a * a for a in left))
    right_norm = math.sqrt(sum(b * b for b in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return dot / (left_norm * right_norm)


def create_vector_store() -> PostgresVectorStore | MemoryVectorStore:
    backend = get_settings().storage_backend.lower()
    if backend == "memory":
        return MemoryVectorStore()
    if backend == "postgres":
        return PostgresVectorStore()
    raise ValueError("STORAGE_BACKEND must be either 'postgres' or 'memory'.")


vector_store = create_vector_store()
