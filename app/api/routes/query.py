"""Q&A endpoints with citation support and query caching."""

from __future__ import annotations

import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Document, DocumentStatus
from app.db.session import get_db
from app.models.schemas import CitationSchema, QueryRequest, QueryResponse
from app.services.cache import get_cached_query, set_cached_query
from app.services.query_engine import query_document

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/query", tags=["query"])


@router.post("/{document_id}", response_model=QueryResponse)
async def ask_question(
    document_id: uuid.UUID,
    body: QueryRequest,
    db: AsyncSession = Depends(get_db),
) -> QueryResponse:
    doc = await db.get(Document, document_id)
    if not doc:
        raise HTTPException(404, "Document not found")

    if doc.status != DocumentStatus.READY:
        raise HTTPException(
            409,
            f"Document is not ready for queries (status: {doc.status.value})",
        )

    cached = get_cached_query(str(document_id), body.question)
    if cached:
        return QueryResponse(
            answer=cached.answer,
            citations=[CitationSchema(**c.__dict__) for c in cached.citations],
            cached=True,
            document_id=document_id,
        )

    try:
        result = query_document(str(document_id), body.question)
    except FileNotFoundError as exc:
        raise HTTPException(409, "Document index is missing. Please re-upload the file.") from exc
    except Exception as exc:
        message = str(exc)
        logger.exception("Query failed for document %s", document_id)
        if "not found" in message.lower() and "model" in message.lower():
            raise HTTPException(
                503,
                "Local LLM model is not available. Run: ollama pull llama3",
            ) from exc
        if "connection" in message.lower() or "11434" in message:
            raise HTTPException(
                503,
                "Cannot reach Ollama. Make sure the Ollama app is running.",
            ) from exc
        raise HTTPException(500, f"Query failed: {message[:300]}") from exc

    set_cached_query(str(document_id), body.question, result)

    return QueryResponse(
        answer=result.answer,
        citations=[CitationSchema(**c.__dict__) for c in result.citations],
        cached=False,
        document_id=document_id,
    )
