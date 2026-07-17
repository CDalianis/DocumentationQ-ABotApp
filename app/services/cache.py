"""In-memory query cache with TTL (no Redis)."""

from __future__ import annotations

import hashlib
import time
from threading import Lock

from app.config import Settings, get_settings
from app.services.query_engine import Citation, QueryResult

_lock = Lock()
_store: dict[str, tuple[float, dict]] = {}


def _cache_key(document_id: str, question: str) -> str:
    digest = hashlib.sha256(question.lower().strip().encode()).hexdigest()[:16]
    return f"qa:{document_id}:{digest}"


def _purge_expired(now: float) -> None:
    expired = [k for k, (expires, _) in _store.items() if expires <= now]
    for key in expired:
        del _store[key]


def get_cached_query(
    document_id: str,
    question: str,
    settings: Settings | None = None,
) -> QueryResult | None:
    settings = settings or get_settings()
    key = _cache_key(document_id, question)
    now = time.monotonic()

    with _lock:
        _purge_expired(now)
        entry = _store.get(key)
        if not entry:
            return None
        _, data = entry

    return QueryResult(
        answer=data["answer"],
        citations=[Citation(**c) for c in data["citations"]],
        cached=True,
    )


def set_cached_query(
    document_id: str,
    question: str,
    result: QueryResult,
    settings: Settings | None = None,
) -> None:
    settings = settings or get_settings()
    key = _cache_key(document_id, question)
    expires = time.monotonic() + settings.query_cache_ttl_seconds
    payload = {
        "answer": result.answer,
        "citations": [
            {"page_number": c.page_number, "source": c.source, "excerpt": c.excerpt}
            for c in result.citations
        ],
    }
    with _lock:
        _store[key] = (expires, payload)


def invalidate_document_cache(document_id: str, settings: Settings | None = None) -> None:
    prefix = f"qa:{document_id}:"
    with _lock:
        for key in [k for k in _store if k.startswith(prefix)]:
            del _store[key]


def clear_cache() -> None:
    """Test helper – wipe the in-memory cache."""
    with _lock:
        _store.clear()
