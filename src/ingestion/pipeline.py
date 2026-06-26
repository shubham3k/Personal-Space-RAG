"""Ingestion orchestrator."""

from pathlib import Path

from config.constants import MAX_DOCUMENT_CHARS
from config.settings import settings
from src.ingestion.chunker import TextChunker
from src.ingestion.embedder import LocalEmbedder
from src.ingestion.loaders import DEFAULT_LOADERS
from src.storage.bm25_store import BM25Store
from src.storage.cache import QueryCache
from src.storage.metadata_store import MetadataStore
from src.storage.vector_store import VectorStore
from src.utils.file_utils import is_supported_file, validate_file
from src.utils.text_processing import truncate_chars


class IngestionPipeline:
    def __init__(
        self,
        vector_store: VectorStore | None = None,
        metadata_store: MetadataStore | None = None,
        embedder: LocalEmbedder | None = None,
        chunker: TextChunker | None = None,
        bm25_store: BM25Store | None = None,
        query_cache: QueryCache | None = None,
    ):
        self.vector_store = vector_store or VectorStore()
        self.metadata_store = metadata_store or MetadataStore()
        self.embedder = embedder or LocalEmbedder()
        self.chunker = chunker or TextChunker()
        self.bm25_store = bm25_store or BM25Store()
        self.query_cache = query_cache or QueryCache()
        self.loaders = DEFAULT_LOADERS

    def delete_by_source_path(self, source_path: str) -> None:
        if hasattr(self.vector_store, "delete_by_source_path"):
            self.vector_store.delete_by_source_path(source_path)
        if hasattr(self.bm25_store, "delete_by_source_path"):
            self.bm25_store.delete_by_source_path(source_path)
        if hasattr(self.metadata_store, "delete_by_source_path"):
            self.metadata_store.delete_by_source_path(source_path)

    def ingest_file(self, file_path: str | Path) -> dict:
        path = Path(file_path)
        validate_file(path)
        loader = self._loader_for(path)
        document = loader.load(path)
        document.metadata.setdefault("source", "local_file")
        document.metadata.setdefault("source_path", str(path))
        document.content = truncate_chars(document.content, MAX_DOCUMENT_CHARS)
        if self.metadata_store.has_file_hash(document.file_hash):
            return {"status": "skipped", "reason": "duplicate", "path": str(path)}
        self.delete_by_source_path(str(path))
        chunks = self.chunker.chunk(document)
        embeddings = self.embedder.embed_texts([chunk.content for chunk in chunks])
        self.vector_store.add_chunks(chunks, embeddings)
        self.bm25_store.add_chunks(chunks)
        self.metadata_store.upsert_document(document, len(chunks))
        self.query_cache.invalidate_all()
        return {"status": "ingested", "path": str(path), "chunks": len(chunks)}

    def ingest_directory(self, directory: str | Path | None = None) -> dict:
        root = Path(directory or settings.raw_data_dir)
        results = []
        for path in root.rglob("*"):
            if is_supported_file(path):
                try:
                    results.append(self.ingest_file(path))
                except Exception as exc:
                    results.append({"status": "error", "path": str(path), "error": str(exc)})
        return {
            "total": len(results),
            "ingested": sum(1 for item in results if item["status"] == "ingested"),
            "skipped": sum(1 for item in results if item["status"] == "skipped"),
            "errors": [item for item in results if item["status"] == "error"],
            "results": results,
        }

    def _loader_for(self, path: Path):
        for loader in self.loaders:
            if loader.can_load(path):
                return loader
        raise ValueError(f"No loader for {path.suffix}")
