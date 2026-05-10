import asyncio
import logging

from fastapi import APIRouter, HTTPException

from app.models.schemas import IngestRequest, IngestResponse
from app.services.embedder import get_embedder
from app.services.vector_store import vector_store

logger = logging.getLogger(__name__)
router = APIRouter(tags=["ingest"])


@router.post("/ingest", response_model=IngestResponse)
async def ingest(payload: IngestRequest) -> IngestResponse:
    try:
        embedding = await get_embedder().encode(payload.text)
        record_id = await vector_store.insert_record(payload.text, embedding, payload.metadata)
        return IngestResponse(id=record_id)
    except asyncio.TimeoutError as exc:
        raise HTTPException(status_code=503, detail="Embedding model timed out.") from exc
    except Exception as exc:
        logger.exception("Failed to ingest record.")
        raise HTTPException(status_code=503, detail="Unable to store record.") from exc
