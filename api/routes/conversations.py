"""Conversation endpoints."""

from fastapi import APIRouter

from src.storage.conversation_store import ConversationStore

router = APIRouter(prefix="/conversations", tags=["conversations"])
store = ConversationStore()


@router.get("/{conversation_id}")
def conversation(conversation_id: str):
    return {"conversation_id": conversation_id, "messages": store.get_messages(conversation_id)}
