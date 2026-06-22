"""Document endpoints."""

from fastapi import APIRouter

from src.storage.metadata_store import MetadataStore

router = APIRouter(prefix="/documents", tags=["documents"])
store = MetadataStore()


@router.get("")
def documents():
    return {"documents": store.list_documents(), "count": store.count()}
