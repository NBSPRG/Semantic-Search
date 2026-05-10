import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import get_settings
from app.db.connection import database
from app.models.schemas import HealthResponse
from app.routes import ingest, search
from app.services.embedder import get_embedder

STATIC_DIR = Path(__file__).resolve().parent / "static"


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    logging.basicConfig(level=settings.log_level)
    get_embedder()
    if settings.storage_backend.lower() == "postgres":
        await database.connect()
    try:
        yield
    finally:
        if settings.storage_backend.lower() == "postgres":
            await database.close()


app = FastAPI(
    title="Mini ML Similarity System",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(ingest.router)
app.include_router(search.router)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
async def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    settings = get_settings()
    db_ok = True
    if settings.storage_backend.lower() == "postgres":
        db_ok = await database.ping()
    model_loaded = get_embedder().is_loaded
    return HealthResponse(
        status="ok" if db_ok and model_loaded else "degraded",
        database=db_ok,
        model_loaded=model_loaded,
        storage_backend=settings.storage_backend.lower(),
    )
