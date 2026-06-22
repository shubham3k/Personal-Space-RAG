"""End-to-end RAG pipeline."""

from src.generation.generator import AnswerGenerator
from src.orchestrator.conversation_manager import ConversationManager
from src.orchestrator.guardrails import validate_user_query
from src.retrieval.retriever import Retriever


class RAGPipeline:
    def __init__(
        self,
        retriever: Retriever | None = None,
        generator: AnswerGenerator | None = None,
        conversations: ConversationManager | None = None,
    ):
        self.retriever = retriever or Retriever()
        self.generator = generator or AnswerGenerator()
        self.conversations = conversations or ConversationManager()

    async def ask(self, query: str, conversation_id: str | None = None, top_k: int | None = None) -> dict:
        query = validate_user_query(query)
        conversation_id = conversation_id or self.conversations.new_id()
        contexts = self.retriever.retrieve(query, top_k=top_k)
        result = await self.generator.generate(query, contexts)
        self.conversations.remember(conversation_id, "user", query)
        self.conversations.remember(conversation_id, "assistant", result["answer"], result.get("provider"))
        return {"conversation_id": conversation_id, **result}
