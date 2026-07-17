"""Local on-disk vector indexes via LlamaIndex (no Postgres/pgvector)."""

from __future__ import annotations

import logging
import shutil
from pathlib import Path

from llama_index.core import Settings as LlamaSettings
from llama_index.core import StorageContext, VectorStoreIndex, load_index_from_storage
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.schema import TextNode

from app.config import Settings, get_settings
from app.services.embeddings import get_embed_model
from app.services.llm import get_llm
from app.services.parser import parse_document

logger = logging.getLogger(__name__)


def _configure_llama(settings: Settings) -> None:
    LlamaSettings.llm = get_llm(settings)
    LlamaSettings.embed_model = get_embed_model(settings)
    LlamaSettings.chunk_size = settings.chunk_size
    LlamaSettings.chunk_overlap = settings.chunk_overlap


def _persist_dir(document_id: str, settings: Settings) -> Path:
    path = settings.vector_store_path / document_id
    path.mkdir(parents=True, exist_ok=True)
    return path


def index_document(
    document_id: str,
    file_path: Path,
    settings: Settings | None = None,
) -> int:
    """Parse, chunk, embed, and persist a document index. Returns node count."""
    settings = settings or get_settings()
    _configure_llama(settings)

    raw_docs = parse_document(file_path)
    splitter = SentenceSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )

    nodes: list[TextNode] = []
    for doc in raw_docs:
        for node in splitter.get_nodes_from_documents([doc]):
            node.metadata["document_id"] = document_id
            node.metadata.setdefault("page_number", doc.metadata.get("page_number", 1))
            node.metadata.setdefault("source", doc.metadata.get("source", file_path.name))
            nodes.append(node)

    persist_dir = _persist_dir(document_id, settings)
    index = VectorStoreIndex(nodes)
    index.storage_context.persist(persist_dir=str(persist_dir))

    logger.info("Indexed %d nodes for document %s → %s", len(nodes), document_id, persist_dir)
    return len(nodes)


def get_query_index(document_id: str, settings: Settings | None = None) -> VectorStoreIndex:
    settings = settings or get_settings()
    _configure_llama(settings)

    persist_dir = settings.vector_store_path / document_id
    if not persist_dir.exists() or not any(persist_dir.iterdir()):
        raise FileNotFoundError(f"No vector index found for document {document_id}")

    storage_context = StorageContext.from_defaults(persist_dir=str(persist_dir))
    return load_index_from_storage(storage_context)


def delete_document_vectors(document_id: str, settings: Settings | None = None) -> None:
    settings = settings or get_settings()
    persist_dir = settings.vector_store_path / document_id
    if persist_dir.exists():
        shutil.rmtree(persist_dir)
