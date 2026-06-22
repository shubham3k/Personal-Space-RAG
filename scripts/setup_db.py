"""Initialize local data directories and SQLite databases."""

from config.settings import settings
from src.storage.conversation_store import ConversationStore
from src.storage.metadata_store import MetadataStore


def main() -> None:
    settings.ensure_directories()
    MetadataStore()
    ConversationStore()
    print("Local directories and SQLite databases are ready.")


if __name__ == "__main__":
    main()
