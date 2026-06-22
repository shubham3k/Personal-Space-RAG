"""ChromaDB vector store wrapper."""

from typing import Any

from config.settings import settings
from src.ingestion.chunker import DocumentChunk


class VectorStore:
    def __init__(self, persist_dir: str | None = None, collection_name: str | None = None):
        import chromadb

        self.client = chromadb.PersistentClient(path=persist_dir or settings.chroma_persist_dir)
        self.collection = self.client.get_or_create_collection(
            name=collection_name or settings.chroma_collection,
            metadata={"hnsw:space": settings.chroma_distance_metric},
        )

    def add_chunks(self, chunks: list[DocumentChunk], embeddings: list[list[float]]) -> None:
        if not chunks:
            return
        self.collection.upsert(
            ids=[chunk.id for chunk in chunks],
            documents=[chunk.content for chunk in chunks],
            metadatas=[self._clean_metadata({**chunk.metadata, "source_path": chunk.source_path, "chunk_index": chunk.chunk_index}) for chunk in chunks],
            embeddings=embeddings,
        )

    def query(self, embedding: list[float], top_k: int | None = None, where: dict | None = None) -> list[dict[str, Any]]:
        result = self.collection.query(
            query_embeddings=[embedding],
            n_results=top_k or settings.retrieval_top_k,
            where=where,
            include=["documents", "metadatas", "distances"],
        )
        documents = result.get("documents", [[]])[0]
        metadatas = result.get("metadatas", [[]])[0]
        distances = result.get("distances", [[]])[0]
        ids = result.get("ids", [[]])[0]
        matches = []
        for idx, document in enumerate(documents):
            distance = distances[idx] if idx < len(distances) else 1.0
            matches.append(
                {
                    "id": ids[idx] if idx < len(ids) else "",
                    "content": document,
                    "metadata": metadatas[idx] if idx < len(metadatas) else {},
                    "distance": distance,
                    "score": max(0.0, 1.0 - float(distance)),
                }
            )
        return matches

    def count(self) -> int:
        return self.collection.count()

    def reset(self) -> None:
        self.client.delete_collection(settings.chroma_collection)
        self.collection = self.client.get_or_create_collection(name=settings.chroma_collection)

    def _clean_metadata(self, metadata: dict) -> dict:
        clean = {}
        for key, value in metadata.items():
            if isinstance(value, (str, int, float, bool)) or value is None:
                clean[key] = value
            elif isinstance(value, list):
                clean[key] = ", ".join(str(item) for item in value)
            else:
                clean[key] = str(value)
        return clean
