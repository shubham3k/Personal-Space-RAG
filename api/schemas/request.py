"""Request models."""

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    query: str = Field(min_length=2, max_length=2000)
    conversation_id: str | None = None
    top_k: int | None = Field(default=None, ge=1, le=50)
    sources: list[str] | None = None


class IngestRequest(BaseModel):
    path: str | None = None


class MemoryRequest(BaseModel):
    type: str = "preference"
    key: str
    value: str
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    source: str = "user"


class FeedbackRequest(BaseModel):
    conversation_id: str | None = None
    rating: str
    comment: str = ""


class IntegrationSettingsRequest(BaseModel):
    settings: dict = {}


class DigestGenerateRequest(BaseModel):
    type: str = "weekly"
    period_start: str | None = None
    period_end: str | None = None
