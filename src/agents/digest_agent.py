"""Digest generation agent."""

from datetime import date, timedelta

from src.generation.generator import AnswerGenerator
from src.retrieval.retriever import Retriever
from src.storage.v3_store import DigestStore


class DigestAgent:
    def __init__(self, retriever: Retriever | None = None, generator: AnswerGenerator | None = None):
        self.retriever = retriever or Retriever()
        self.generator = generator or AnswerGenerator()
        self.store = DigestStore()

    async def generate(self, digest_type: str = "weekly", period_start: str | None = None, period_end: str | None = None) -> dict:
        today = date.today()
        if period_end is None:
            period_end = today.isoformat()
        if period_start is None:
            days = 1 if digest_type == "daily" else 7 if digest_type == "weekly" else 30
            period_start = (today - timedelta(days=days - 1)).isoformat()
        query = f"{digest_type} digest from {period_start} to {period_end}: activity summary, themes, highlights, progress, anomalies"
        contexts = self.retriever.retrieve(query, top_k=30)
        result = await self.generator.generate(query, contexts)
        self.store.upsert(digest_type, period_start, period_end, result["answer"])
        return {"period_start": period_start, "period_end": period_end, **result}
