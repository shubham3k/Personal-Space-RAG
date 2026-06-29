"""Cross-encoder reranking."""

from config.settings import settings


class CrossEncoderReranker:
    def __init__(self):
        self._model = None

    def rerank(self, query: str, results: list[dict], top_k: int | None = None) -> list[dict]:
        if not settings.reranker_enabled or not results:
            return results[: top_k or settings.reranker_top_k]
        try:
            model = self._get_model()
            pairs = [(query, item["content"][:2048]) for item in results]
            scores = model.predict(pairs)
            reranked = []
            for item, score in zip(results, scores):
                reranked.append({**item, "rerank_score": float(score), "score": float(score)})
            reranked.sort(key=lambda item: item["rerank_score"], reverse=True)
            return reranked[: top_k or settings.reranker_top_k]
        except Exception:
            return results[: top_k or settings.reranker_top_k]

    def _get_model(self):
        if self._model is None:
            from sentence_transformers import CrossEncoder

            self._model = CrossEncoder(settings.reranker_model, device=settings.reranker_device)
        return self._model
