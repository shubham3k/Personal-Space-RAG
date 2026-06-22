"""Query endpoints."""

from fastapi import APIRouter

from api.schemas.request import QueryRequest
from src.orchestrator.rag_pipeline import RAGPipeline

router = APIRouter(prefix="/query", tags=["query"])
pipeline = RAGPipeline()


@router.post("")
async def query(request: QueryRequest):
    return await pipeline.ask(request.query, conversation_id=request.conversation_id, top_k=request.top_k)
