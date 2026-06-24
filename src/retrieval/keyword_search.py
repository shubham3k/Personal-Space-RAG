"""Keyword search via persistent BM25."""

from config.settings import settings
from src.storage.bm25_store import BM25Store


class KeywordSearch:
    def __init__(self, store: BM25Store | None = None):
        self.store = store or BM25Store()

    def search(self, query: str, top_k: int | None = None, filters: dict | None = None) -> list[dict]:
        if not settings.bm25_enabled:
            return []
        return self.store.search(query, top_k=top_k or settings.retrieval_top_k, filters=filters)
