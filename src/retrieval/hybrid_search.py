"""Hybrid dense+sparse retrieval with reciprocal rank fusion."""

from config.settings import settings
from src.retrieval.keyword_search import KeywordSearch
from src.retrieval.semantic_search import SemanticSearch


class HybridSearch:
    def __init__(self, semantic: SemanticSearch | None = None, keyword: KeywordSearch | None = None):
        self.semantic = semantic or SemanticSearch()
        self.keyword = keyword or KeywordSearch()

    def search(self, query: str, top_k: int | None = None, filters: dict | None = None) -> list[dict]:
        requested = top_k or settings.retrieval_top_k
        dense = self.semantic.search(query, top_k=max(requested * 2, requested), media_type=filters.get("media_type") if filters else None)
        sparse = self.keyword.search(query, top_k=max(requested * 2, requested), filters=filters)
        return reciprocal_rank_fusion(dense, sparse, top_k=requested)


def reciprocal_rank_fusion(dense: list[dict], sparse: list[dict], top_k: int, k: int = 60) -> list[dict]:
    fused: dict[str, dict] = {}
    for method, results, weight in (
        ("semantic", dense, 1.0 - settings.bm25_weight),
        ("bm25", sparse, settings.bm25_weight),
    ):
        for rank, item in enumerate(results, start=1):
            item_id = item.get("id") or item.get("chunk_id")
            if not item_id:
                continue
            if item_id not in fused:
                fused[item_id] = {**item, "score": 0.0, "retrieval_methods": []}
            fused[item_id]["score"] += weight * (1.0 / (k + rank))
            fused[item_id]["retrieval_methods"].append(method)
    ranked = sorted(fused.values(), key=lambda item: item["score"], reverse=True)
    return ranked[:top_k]
