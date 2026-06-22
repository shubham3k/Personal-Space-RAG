"""Semantic search service."""

from config.settings import settings
from src.ingestion.embedder import LocalEmbedder
from src.retrieval.filters import build_where_filter
from src.retrieval.query_processor import QueryProcessor
from src.storage.vector_store import VectorStore


class SemanticSearch:
    def __init__(self, vector_store: VectorStore | None = None, embedder: LocalEmbedder | None = None):
        self.vector_store = vector_store or VectorStore()
        self.embedder = embedder or LocalEmbedder()
        self.processor = QueryProcessor()

    def search(self, query: str, top_k: int | None = None, doc_type: str | None = None) -> list[dict]:
        normalized = self.processor.normalize(query)
        embedding = self.embedder.embed_query(normalized)
        matches = self.vector_store.query(embedding, top_k=top_k or settings.retrieval_top_k, where=build_where_filter(doc_type=doc_type))
        return [match for match in matches if match["score"] >= settings.similarity_threshold]
