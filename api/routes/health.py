"""Health endpoint."""

from fastapi import APIRouter

from config.settings import settings
from src.generation.llm_client import LLMClient
from src.storage.bm25_store import BM25Store
from src.storage.cache import QueryCache
from src.storage.metadata_store import MetadataStore
from src.storage.vector_store import VectorStore
from src.storage.schema import EXPECTED_SCHEMA_VERSION
from src.automation.scheduler import JobStore

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
        "bm25_chunks": BM25Store().count(),
        "cache": QueryCache().stats(),
        "features": {
            "bm25_enabled": settings.bm25_enabled,
            "reranker_enabled": settings.reranker_enabled,
            "cache_enabled": settings.cache_enabled,
            "vision_enabled": settings.vision_enabled,
            "agentic_v3_enabled": True,
        },
        "schema_version": EXPECTED_SCHEMA_VERSION,
        "scheduled_jobs": JobStore().list(),
    }
