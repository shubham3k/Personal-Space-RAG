"""Lightweight RAG evaluation metrics."""

from dataclasses import dataclass


@dataclass
class EvalResult:
    query: str
    answer: str
    contexts: list[str]
    relevance: float = 0.0
    context_precision: float = 0.0


class RAGEvaluator:
    def evaluate_context_precision(self, contexts: list[str], query: str) -> float:
        if not contexts:
            return 0.0
        query_terms = {term.lower() for term in query.split() if len(term) > 2}
        if not query_terms:
            return 0.0
        relevant = 0
        for context in contexts:
            context_lower = context.lower()
            matches = sum(1 for term in query_terms if term in context_lower)
            if matches / len(query_terms) >= 0.3:
                relevant += 1
        return relevant / len(contexts)

    def evaluate_relevance(self, query: str, answer: str) -> float:
        answer_lower = answer.lower()
        query_terms = {term.lower() for term in query.split() if len(term) > 2}
        if not query_terms or not answer:
            return 0.0
        return sum(1 for term in query_terms if term in answer_lower) / len(query_terms)

    def evaluate_single(self, query: str, answer: str, contexts: list[str]) -> EvalResult:
        return EvalResult(
            query=query,
            answer=answer,
            contexts=contexts,
            relevance=self.evaluate_relevance(query, answer),
            context_precision=self.evaluate_context_precision(contexts, query),
        )
