import asyncio
import logging

from fastapi import APIRouter, HTTPException

from app.models.schemas import SearchRequest, SearchResponse
from app.services.embedder import get_embedder
from app.services.vector_store import vector_store

logger = logging.getLogger(__name__)
router = APIRouter(tags=["search"])


@router.post("/search", response_model=SearchResponse)
async def search(payload: SearchRequest) -> SearchResponse:
    try:
        embedding = await get_embedder().encode(payload.query)
        results = await vector_store.search(embedding, payload.top_k)
        return SearchResponse(results=results)
    except asyncio.TimeoutError as exc:
        raise HTTPException(status_code=503, detail="Embedding model timed out.") from exc
    except Exception as exc:
        logger.exception("Failed to search records.")
        raise HTTPException(status_code=503, detail="Unable to search records.") from exc
