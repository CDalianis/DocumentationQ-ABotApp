"""Document upload and management endpoints."""

from __future__ import annotations

import uuid
from pathlib import Path

import aiofiles
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Response, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.db.models import Document, DocumentStatus
from app.db.session import get_db
from app.models.schemas import DocumentResponse, DocumentUploadResponse
from app.services.indexer import delete_document_vectors
from app.services.parser import SUPPORTED_EXTENSIONS
from app.services.processing import process_document

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=DocumentUploadResponse, status_code=202)
async def upload_document(
    file: UploadFile,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> DocumentUploadResponse:
    settings = get_settings()

    if not file.filename:
        raise HTTPException(400, "Filename is required")

    suffix = Path(file.filename).suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            400,
            f"Unsupported file type '{suffix}'. Supported: {', '.join(sorted(SUPPORTED_EXTENSIONS))}",
        )

    content = await file.read()
    if len(content) > settings.max_upload_bytes:
        raise HTTPException(400, f"File exceeds {settings.max_upload_size_mb} MB limit")

    doc_id = uuid.uuid4()
    settings.upload_path.mkdir(parents=True, exist_ok=True)
    dest = settings.upload_path / f"{doc_id}{suffix}"

    async with aiofiles.open(dest, "wb") as f:
        await f.write(content)

    doc = Document(
        id=doc_id,
        filename=file.filename,
        file_path=str(dest),
        status=DocumentStatus.PENDING,
    )
    db.add(doc)
    await db.commit()

    background_tasks.add_task(process_document, str(doc_id))

    return DocumentUploadResponse(
        id=doc_id,
        filename=file.filename,
        status=DocumentStatus.PENDING.value,
        message="Document queued for processing. Poll GET /documents/{id} for status.",
    )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> DocumentResponse:
    doc = await db.get(Document, document_id)
    if not doc:
        raise HTTPException(404, "Document not found")
    return DocumentResponse.model_validate(doc)


@router.get("/", response_model=list[DocumentResponse])
async def list_documents(db: AsyncSession = Depends(get_db)) -> list[DocumentResponse]:
    result = await db.execute(select(Document).order_by(Document.created_at.desc()))
    return [DocumentResponse.model_validate(d) for d in result.scalars().all()]


@router.delete("/{document_id}", status_code=204, response_class=Response)
async def delete_document(
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> Response:
    doc = await db.get(Document, document_id)
    if not doc:
        raise HTTPException(404, "Document not found")

    try:
        delete_document_vectors(str(document_id))
    except Exception:
        pass

    file_path = Path(doc.file_path)
    if file_path.exists():
        file_path.unlink()

    await db.delete(doc)
    await db.commit()
    return Response(status_code=204)
