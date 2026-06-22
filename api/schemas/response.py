"""Response models."""

from pydantic import BaseModel


class Source(BaseModel):
    number: int
    title: str
    source_path: str
    score: float


class QueryResponse(BaseModel):
    conversation_id: str
    answer: str
    provider: str
    model: str
    sources: list[Source]
    usage: dict
