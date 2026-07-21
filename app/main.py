"""Context-Aware Documentation Q&A Bot – FastAPI entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import documents, query
from app.config import get_settings
from app.db.session import init_db
from app.models.schemas import HealthResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    settings.upload_path.mkdir(parents=True, exist_ok=True)
    settings.vector_store_path.mkdir(parents=True, exist_ok=True)
    await init_db()
    yield


app = FastAPI(
    title="Documentation Q&A Bot",
    description=(
        "Upload PDF/Word documents and ask questions answered strictly "
        "from document content with page-number citations. "
        "Runs fully local with Ollama + SQLite (no Docker required)."
    ),
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents.router, prefix="/api/v1")
app.include_router(query.router, prefix="/api/v1")


@app.get("/health", response_model=HealthResponse, tags=["health"])
async def health() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(
        status="ok",
        llm_provider=settings.llm_provider,
        embedding_provider=settings.embedding_provider,
    )
