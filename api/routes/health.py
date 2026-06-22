"""Health endpoint."""

from fastapi import APIRouter

from config.settings import settings
from src.generation.llm_client import LLMClient
from src.storage.metadata_store import MetadataStore
from src.storage.vector_store import VectorStore

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
async def health():
    llm = LLMClient()
    return {
        "status": "ok",
        "configured_providers": settings.available_providers,
        "provider_health": await llm.health(),
        "documents": MetadataStore().count(),
        "chunks": VectorStore().count(),
    }
