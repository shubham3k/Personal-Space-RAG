"""Reflection agent for patterns and themes."""

from src.generation.generator import AnswerGenerator
from src.retrieval.retriever import Retriever
from src.storage.v3_store import InsightStore


class ReflectionAgent:
    def __init__(self, retriever: Retriever | None = None, generator: AnswerGenerator | None = None):
        self.retriever = retriever or Retriever()
        self.generator = generator or AnswerGenerator()
        self.insights = InsightStore()

    async def run(self, query: str) -> dict:
        contexts = self.retriever.retrieve(query, top_k=30)
        if len(contexts) < 3:
            answer = "I need more indexed material to identify reliable patterns. Keep adding notes and connected sources."
            return {"answer": answer, "provider": "local", "model": "reflection-agent", "sources": [], "usage": {}}
        result = await self.generator.generate(
            "Analyze recurring patterns, themes, weak signals, and concrete suggestions for: " + query,
            contexts,
        )
        self.insights.add("reflection", result["answer"], result.get("sources", []))
        return result
