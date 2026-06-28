"""Initialize local data directories and SQLite databases."""

from config.settings import settings
from src.automation.scheduler import JobStore
from src.storage.bm25_store import BM25Store
from src.storage.cache import QueryCache
from src.storage.conversation_store import ConversationStore
from src.storage.metadata_store import MetadataStore
from src.storage.schema import SchemaManager


def main() -> None:
    settings.ensure_directories()
    MetadataStore()
    ConversationStore()
    SchemaManager().migrate()
    JobStore().ensure_defaults()
    BM25Store()
    QueryCache()
    print("Local directories and SQLite databases are ready.")


if __name__ == "__main__":
    main()
