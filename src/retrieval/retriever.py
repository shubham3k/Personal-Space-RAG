"""High-level retriever."""

from config.settings import settings
from src.retrieval.hybrid_search import HybridSearch
from src.retrieval.reranker import CrossEncoderReranker
from src.retrieval.semantic_search import SemanticSearch


class Retriever:
    def __init__(self, search: SemanticSearch | None = None, hybrid: HybridSearch | None = None, reranker: CrossEncoderReranker | None = None):
        self.search_service = hybrid or HybridSearch(semantic=search) if settings.bm25_enabled else search or SemanticSearch()
        self.reranker = reranker or CrossEncoderReranker()

    def retrieve(self, query: str, top_k: int | None = None, sources: list[str] | None = None) -> list[dict]:
        results = self.search_service.search(query, top_k=max(top_k or settings.retrieval_top_k, settings.reranker_top_k))
        if sources:
            allowed = set(sources)
            results = [item for item in results if item.get("metadata", {}).get("source") in allowed]
        return self.reranker.rerank(query, results, top_k=top_k or settings.reranker_top_k)
