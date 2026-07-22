import uuid

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_upload_docx(client: AsyncClient, sample_docx):
    with sample_docx.open("rb") as f:
        res = await client.post(
            "/api/v1/documents/upload",
            files={"file": ("manual.docx", f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
        )

    assert res.status_code == 202
    data = res.json()
    assert data["filename"] == "manual.docx"
    assert data["status"] == "pending"
    assert uuid.UUID(data["id"])
    client.mock_process.assert_called_once_with(data["id"])  # type: ignore[attr-defined]


@pytest.mark.asyncio
async def test_upload_rejects_unsupported_type(client: AsyncClient):
    res = await client.post(
        "/api/v1/documents/upload",
        files={"file": ("notes.txt", b"hello", "text/plain")},
    )
    assert res.status_code == 400
    assert "Unsupported" in res.json()["detail"]


@pytest.mark.asyncio
async def test_get_and_list_documents(client: AsyncClient, sample_docx):
    with sample_docx.open("rb") as f:
        upload = await client.post(
            "/api/v1/documents/upload",
            files={"file": ("manual.docx", f, "application/octet-stream")},
        )
    doc_id = upload.json()["id"]

    get_res = await client.get(f"/api/v1/documents/{doc_id}")
    assert get_res.status_code == 200
    assert get_res.json()["filename"] == "manual.docx"

    list_res = await client.get("/api/v1/documents/")
    assert list_res.status_code == 200
    assert len(list_res.json()) == 1


@pytest.mark.asyncio
async def test_get_document_not_found(client: AsyncClient):
    res = await client.get(f"/api/v1/documents/{uuid.uuid4()}")
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_delete_document(client: AsyncClient, sample_docx):
    with sample_docx.open("rb") as f:
        upload = await client.post(
            "/api/v1/documents/upload",
            files={"file": ("manual.docx", f, "application/octet-stream")},
        )
    doc_id = upload.json()["id"]

    del_res = await client.delete(f"/api/v1/documents/{doc_id}")
    assert del_res.status_code == 204

    get_res = await client.get(f"/api/v1/documents/{doc_id}")
    assert get_res.status_code == 404
