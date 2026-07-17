from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class DocumentResponse(BaseModel):
    id: uuid.UUID
    filename: str
    status: str
    node_count: int | None = None
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DocumentUploadResponse(BaseModel):
    id: uuid.UUID
    filename: str
    status: str
    message: str


class CitationSchema(BaseModel):
    page_number: int
    source: str
    excerpt: str


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=2000)


class QueryResponse(BaseModel):
    answer: str
    citations: list[CitationSchema]
    cached: bool = False
    document_id: uuid.UUID


class HealthResponse(BaseModel):
    status: str
    llm_provider: str
    embedding_provider: str
