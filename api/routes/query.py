"""Query endpoints."""

from fastapi import APIRouter

from api.schemas.request import QueryRequest
from src.agents.agent_orchestrator import AgentOrchestrator

router = APIRouter(prefix="/query", tags=["query"])
pipeline = AgentOrchestrator()


@router.post("")
async def query(request: QueryRequest):
    return await pipeline.ask(request.query, conversation_id=request.conversation_id, top_k=request.top_k, sources=request.sources)
