"""Agentic router in front of the RAG pipeline."""

from src.agents.connection_agent import ConnectionAgent
from src.agents.digest_agent import DigestAgent
from src.agents.intent_router import Intent, IntentRouter
from src.agents.planner import MultiStepPlannerAgent
from src.agents.preparation_agent import PreparationAgent
from src.agents.reflection_agent import ReflectionAgent
from src.orchestrator.rag_pipeline import RAGPipeline
from src.storage.metadata_store import MetadataStore


class AgentOrchestrator:
    def __init__(self):
        self.router = IntentRouter()
        self.rag = RAGPipeline()
        self.planner = MultiStepPlannerAgent()
        self.reflection = ReflectionAgent()
        self.connection = ConnectionAgent()
        self.digest = DigestAgent()
        self.preparation = PreparationAgent()

    async def ask(self, query: str, conversation_id: str | None = None, top_k: int | None = None, sources: list[str] | None = None) -> dict:
        route = self.router.classify(query)
        if route.intent == Intent.CONVERSATIONAL:
            return {"conversation_id": conversation_id or "", "answer": "I can search your knowledge base, generate digests, prepare briefs, find patterns, and sync connected sources.", "provider": "local", "model": "intent-router", "sources": [], "usage": {}, "intent": route.intent}
        if route.intent == Intent.META:
            count = MetadataStore().count()
            return {"conversation_id": conversation_id or "", "answer": f"You currently have {count} indexed documents.", "provider": "local", "model": "metadata", "sources": [], "usage": {}, "intent": route.intent}
        if route.intent == Intent.COMMAND:
            return {"conversation_id": conversation_id or "", "answer": "Command routing is available through the API endpoints: /ingest, /v1/integrations/{id}/sync, and /v1/memory.", "provider": "local", "model": "command-router", "sources": [], "usage": {}, "intent": route.intent}
        if route.intent == Intent.MULTI_STEP:
            result = await self.planner.run(query, top_k=top_k)
        elif route.intent == Intent.REFLECTION:
            result = await self.reflection.run(query)
        elif route.intent == Intent.CONNECTION:
            result = await self.connection.run(query)
        elif route.intent == Intent.SYNTHESIS:
            result = await self.digest.generate("weekly")
        elif route.intent == Intent.PREPARATION:
            result = await self.preparation.run(query)
        else:
            result = await self.rag.ask(query, conversation_id=conversation_id, top_k=top_k, sources=sources)
        result["intent"] = route.intent
        result["intent_confidence"] = route.confidence
        return result
