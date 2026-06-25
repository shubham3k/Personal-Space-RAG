"""Connection discovery agent."""

from src.generation.generator import AnswerGenerator
from src.retrieval.retriever import Retriever
from src.storage.v3_store import InsightStore


class ConnectionAgent:
    def __init__(self, retriever: Retriever | None = None, generator: AnswerGenerator | None = None):
        self.retriever = retriever or Retriever()
        self.generator = generator or AnswerGenerator()
        self.insights = InsightStore()

    async def run(self, query: str) -> dict:
        contexts = self.retriever.retrieve(query, top_k=20)
        if not contexts:
            return {"answer": "I do not have enough information to identify a meaningful connection yet.", "provider": "local", "model": "connection-agent", "sources": [], "usage": {}}
        result = await self.generator.generate(
            "Find meaningful, non-obvious connections. Separate strong evidence from weak signals. Query: " + query,
            contexts,
        )
        self.insights.add("connection", result["answer"], result.get("sources", []))
        return result
