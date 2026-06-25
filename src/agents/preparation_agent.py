"""Meeting and event preparation agent."""

from src.generation.generator import AnswerGenerator
from src.retrieval.retriever import Retriever


class PreparationAgent:
    def __init__(self, retriever: Retriever | None = None, generator: AnswerGenerator | None = None):
        self.retriever = retriever or Retriever()
        self.generator = generator or AnswerGenerator()

    async def run(self, query: str) -> dict:
        contexts = self.retriever.retrieve(query, top_k=20)
        return await self.generator.generate(
            "Create a meeting preparation brief with context, likely agenda, prior mentions, risks, and questions. Request: " + query,
            contexts,
        )
