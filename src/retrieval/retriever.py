"""High-level retriever."""

from src.retrieval.semantic_search import SemanticSearch


class Retriever:
    def __init__(self, search: SemanticSearch | None = None):
        self.search_service = search or SemanticSearch()

    def retrieve(self, query: str, top_k: int | None = None) -> list[dict]:
        return self.search_service.search(query, top_k=top_k)
