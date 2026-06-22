"""Request models."""

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    query: str = Field(min_length=2, max_length=2000)
    conversation_id: str | None = None
    top_k: int | None = Field(default=None, ge=1, le=50)


class IngestRequest(BaseModel):
    path: str | None = None
