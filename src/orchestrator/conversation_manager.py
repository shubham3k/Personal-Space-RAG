"""Conversation persistence helper."""

from uuid import uuid4

from src.storage.conversation_store import ConversationStore


class ConversationManager:
    def __init__(self, store: ConversationStore | None = None):
        self.store = store or ConversationStore()

    def new_id(self) -> str:
        return str(uuid4())

    def remember(self, conversation_id: str, role: str, content: str, provider: str | None = None) -> None:
        self.store.add_message(conversation_id, role, content, provider)

    def history(self, conversation_id: str, limit: int = 20) -> list[dict]:
        return self.store.get_messages(conversation_id, limit)
