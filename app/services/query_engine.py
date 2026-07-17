"""RAG query engine with page-number citations."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from llama_index.core import Settings as LlamaSettings

from app.config import Settings, get_settings
from app.services.embeddings import get_embed_model
from app.services.indexer import get_query_index
from app.services.llm import get_llm

logger = logging.getLogger(__name__)

CITATION_PROMPT = (
    "You are a documentation assistant. Answer the question STRICTLY based on "
    "the provided context. If the answer is not in the context, say "
    "'I cannot find this information in the document.'\n\n"
    "Always cite page numbers in your answer using the format [Page X]. "
    "Include all relevant page citations.\n\n"
    "Context:\n{context_str}\n\n"
    "Question: {query_str}\n\n"
    "Answer:"
)


@dataclass
class Citation:
    page_number: int
    source: str
    excerpt: str


@dataclass
class QueryResult:
    answer: str
    citations: list[Citation] = field(default_factory=list)
    cached: bool = False


def _configure(settings: Settings) -> None:
    LlamaSettings.llm = get_llm(settings)
    LlamaSettings.embed_model = get_embed_model(settings)


def query_document(
    document_id: str,
    question: str,
    settings: Settings | None = None,
    top_k: int = 5,
) -> QueryResult:
    settings = settings or get_settings()
    _configure(settings)

    # Each document has its own on-disk index, so no metadata filter is needed
    # (SimpleVectorStore filters are unreliable and can return zero results).
    index = get_query_index(document_id, settings)
    retriever = index.as_retriever(similarity_top_k=top_k)

    llm = get_llm(settings)
    nodes = retriever.retrieve(question)
    context_parts = []
    citations: list[Citation] = []
    seen_pages: set[tuple[int, str]] = set()

    for node in nodes:
        page = node.metadata.get("page_number", "?")
        source = node.metadata.get("source", "unknown")
        context_parts.append(f"[Page {page}] {node.get_content()}")
        key = (page if isinstance(page, int) else 0, source)
        if key not in seen_pages:
            seen_pages.add(key)
            citations.append(
                Citation(
                    page_number=page if isinstance(page, int) else 0,
                    source=source,
                    excerpt=node.get_content()[:200],
                )
            )

    if not context_parts:
        return QueryResult(
            answer="I cannot find this information in the document.",
            citations=[],
        )

    context_str = "\n\n---\n\n".join(context_parts)
    prompt = CITATION_PROMPT.format(context_str=context_str, query_str=question)

    response = llm.complete(prompt)
    answer = str(response).strip()

    return QueryResult(answer=answer, citations=citations)
