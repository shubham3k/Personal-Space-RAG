"""End-to-end RAG pipeline."""

from src.generation.generator import AnswerGenerator
from src.orchestrator.conversation_manager import ConversationManager
from src.orchestrator.guardrails import validate_user_query
from src.retrieval.retriever import Retriever
from src.storage.cache import QueryCache


class RAGPipeline:
    def __init__(
        self,
        retriever: Retriever | None = None,
        generator: AnswerGenerator | None = None,
        conversations: ConversationManager | None = None,
        cache: QueryCache | None = None,
    ):
        self.retriever = retriever or Retriever()
        self.generator = generator or AnswerGenerator()
        self.conversations = conversations or ConversationManager()
        self.cache = cache or QueryCache()

    async def ask(self, query: str, conversation_id: str | None = None, top_k: int | None = None, sources: list[str] | None = None) -> dict:
        query = validate_user_query(query)
        conversation_id = conversation_id or self.conversations.new_id()
        cached = self.cache.get(query)
        if cached:
            self.conversations.remember(conversation_id, "user", query)
            self.conversations.remember(conversation_id, "assistant", cached["answer"], cached.get("provider"))
            return {"conversation_id": conversation_id, "cached": True, **cached}
        contexts = self.retriever.retrieve(query, top_k=top_k, sources=sources)
        result = await self.generator.generate(query, contexts)
        self.cache.set(query, result)
        self.conversations.remember(conversation_id, "user", query)
        self.conversations.remember(conversation_id, "assistant", result["answer"], result.get("provider"))
        return {"conversation_id": conversation_id, **result}
