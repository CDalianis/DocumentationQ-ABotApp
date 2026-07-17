"""In-process document indexing (no Celery / Redis)."""

from __future__ import annotations

import logging
import uuid
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db.models import Document, DocumentStatus
from app.services.cache import invalidate_document_cache
from app.services.indexer import index_document

logger = logging.getLogger(__name__)


def _sync_session() -> Session:
    """Sync SQLite session for background threads."""
    settings = get_settings()
    url = settings.database_url
    # Convert async SQLite URL → sync
    if url.startswith("sqlite+aiosqlite:///"):
        url = url.replace("sqlite+aiosqlite:///", "sqlite:///", 1)
    elif url.startswith("sqlite+aiosqlite://"):
        url = url.replace("sqlite+aiosqlite://", "sqlite://", 1)
    engine = create_engine(url, connect_args={"check_same_thread": False})
    return Session(engine)


def process_document(document_id: str) -> dict:
    """Parse, embed, and index a document. Safe to run via BackgroundTasks."""
    doc_uuid = uuid.UUID(document_id)
    settings = get_settings()

    with _sync_session() as session:
        doc = session.get(Document, doc_uuid)
        if not doc:
            raise ValueError(f"Document {document_id} not found")

        doc.status = DocumentStatus.PROCESSING
        session.commit()

        try:
            file_path = Path(doc.file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")

            node_count = index_document(document_id, file_path, settings)
            invalidate_document_cache(document_id, settings)

            doc.status = DocumentStatus.READY
            doc.node_count = node_count
            doc.error_message = None
            session.commit()

            logger.info("Document %s indexed with %d nodes", document_id, node_count)
            return {"document_id": document_id, "node_count": node_count, "status": "ready"}

        except Exception as exc:
            logger.exception("Failed to process document %s", document_id)
            doc.status = DocumentStatus.FAILED
            doc.error_message = str(exc)[:2000]
            session.commit()
            raise
