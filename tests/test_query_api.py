import uuid
from unittest.mock import patch

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.db.models import Document, DocumentStatus
from app.services.query_engine import Citation, QueryResult


@pytest.mark.asyncio
async def test_query_ready_document(client: AsyncClient, db_engine, sample_docx):
    factory = async_sessionmaker(db_engine, expire_on_commit=False)
    async with factory() as session:
        doc = Document(
            id=uuid.uuid4(),
            filename="manual.docx",
            file_path=str(sample_docx),
            status=DocumentStatus.READY,
            node_count=3,
        )
        session.add(doc)
        await session.commit()
        doc_id = doc.id

    mock_result = QueryResult(
        answer="The warranty period is 2 years [Page 1].",
        citations=[
            Citation(page_number=1, source="manual.docx", excerpt="warranty period is 2 years"),
        ],
    )

    with (
        patch("app.api.routes.query.get_cached_query", return_value=None),
        patch("app.api.routes.query.query_document", return_value=mock_result),
        patch("app.api.routes.query.set_cached_query"),
    ):
        res = await client.post(
            f"/api/v1/query/{doc_id}",
            json={"question": "What is the warranty period?"},
        )

    assert res.status_code == 200
    data = res.json()
    assert "2 years" in data["answer"]
    assert data["citations"][0]["page_number"] == 1
    assert data["cached"] is False


@pytest.mark.asyncio
async def test_query_returns_cached_response(client: AsyncClient, db_engine):
    factory = async_sessionmaker(db_engine, expire_on_commit=False)
    async with factory() as session:
        doc = Document(
            id=uuid.uuid4(),
            filename="cached.docx",
            file_path="/tmp/cached.docx",
            status=DocumentStatus.READY,
        )
        session.add(doc)
        await session.commit()
        doc_id = doc.id

    cached = QueryResult(
        answer="Cached answer [Page 1].",
        citations=[Citation(page_number=1, source="cached.docx", excerpt="cached")],
        cached=True,
    )

    with patch("app.api.routes.query.get_cached_query", return_value=cached):
        res = await client.post(
            f"/api/v1/query/{doc_id}",
            json={"question": "repeat question"},
        )

    assert res.status_code == 200
    assert res.json()["cached"] is True
    assert res.json()["answer"] == "Cached answer [Page 1]."


@pytest.mark.asyncio
async def test_query_rejects_pending_document(client: AsyncClient, db_engine):
    factory = async_sessionmaker(db_engine, expire_on_commit=False)
    async with factory() as session:
        doc = Document(
            id=uuid.uuid4(),
            filename="pending.pdf",
            file_path="/tmp/pending.pdf",
            status=DocumentStatus.PENDING,
        )
        session.add(doc)
        await session.commit()
        doc_id = doc.id

    res = await client.post(
        f"/api/v1/query/{doc_id}",
        json={"question": "What is this about?"},
    )
    assert res.status_code == 409


@pytest.mark.asyncio
async def test_query_validates_question_length(client: AsyncClient, db_engine):
    factory = async_sessionmaker(db_engine, expire_on_commit=False)
    async with factory() as session:
        doc = Document(
            id=uuid.uuid4(),
            filename="ready.pdf",
            file_path="/tmp/ready.pdf",
            status=DocumentStatus.READY,
        )
        session.add(doc)
        await session.commit()
        doc_id = doc.id

    res = await client.post(f"/api/v1/query/{doc_id}", json={"question": "ab"})
    assert res.status_code == 422
