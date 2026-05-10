from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class IngestRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=10_000)
    metadata: dict[str, Any] = Field(default_factory=dict)


class IngestResponse(BaseModel):
    id: int
    message: str = "Stored successfully"


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=10_000)
    top_k: int = Field(default=5, ge=1, le=50)


class SearchResult(BaseModel):
    id: int
    text: str
    similarity: float
    metadata: dict[str, Any]

    model_config = ConfigDict(from_attributes=True)


class SearchResponse(BaseModel):
    results: list[SearchResult]


class HealthResponse(BaseModel):
    status: str
    database: bool
    model_loaded: bool
    storage_backend: str
