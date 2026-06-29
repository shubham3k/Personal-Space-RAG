"""Persistent BM25 index storage."""

import pickle
import re
from pathlib import Path

from config.settings import settings


class BM25Store:
    def __init__(self, persist_path: str | None = None):
        self.persist_path = Path(persist_path or settings.bm25_index_path)
        self.persist_path.mkdir(parents=True, exist_ok=True)
        self.index_file = self.persist_path / "bm25.pkl"
        self.bm25 = None
        self.chunk_ids: list[str] = []
        self.chunk_contents: list[str] = []
        self.chunk_metadata: list[dict] = []
        self.tokenized_corpus: list[list[str]] = []
        self._load()

    def add_chunks(self, chunks) -> None:
        changed = False
        for chunk in chunks:
            chunk_id = getattr(chunk, "id", chunk.get("id") if isinstance(chunk, dict) else "")
            content = getattr(chunk, "content", chunk.get("content") if isinstance(chunk, dict) else "")
            metadata = getattr(chunk, "metadata", chunk.get("metadata", {}) if isinstance(chunk, dict) else {})
            source_path = getattr(chunk, "source_path", metadata.get("source_path", "") if isinstance(metadata, dict) else "")
            chunk_index = getattr(chunk, "chunk_index", metadata.get("chunk_index", 0) if isinstance(metadata, dict) else 0)
            if not chunk_id or chunk_id in self.chunk_ids:
                continue
            tokens = self._tokenize(content)
            if not tokens:
                continue
            self.chunk_ids.append(chunk_id)
            self.chunk_contents.append(content)
            self.chunk_metadata.append({**metadata, "source_path": source_path, "chunk_index": chunk_index})
            self.tokenized_corpus.append(tokens)
            changed = True
        if changed:
            self._rebuild()
            self._save()

    def search(self, query: str, top_k: int = 20, filters: dict | None = None) -> list[dict]:
        if self.bm25 is None or not self.tokenized_corpus:
            return []
        tokens = self._tokenize(query)
        if not tokens:
            return []
        scores = self.bm25.get_scores(tokens)
        results = []
        for idx, score in enumerate(scores):
            if score <= 0:
                continue
            metadata = self.chunk_metadata[idx]
            if filters and not self._matches_filters(metadata, filters):
                continue
            results.append(
                {
                    "id": self.chunk_ids[idx],
                    "chunk_id": self.chunk_ids[idx],
                    "content": self.chunk_contents[idx],
                    "metadata": metadata,
                    "score": float(score),
                    "retrieval_method": "bm25",
                }
            )
        results.sort(key=lambda item: item["score"], reverse=True)
        return results[:top_k]

    def count(self) -> int:
        return len(self.chunk_ids)

    def delete_by_source_path(self, source_path: str) -> None:
        indices_to_keep = [i for i, meta in enumerate(self.chunk_metadata) if meta.get("source_path") != source_path]
        if len(indices_to_keep) < len(self.chunk_ids):
            self.chunk_ids = [self.chunk_ids[i] for i in indices_to_keep]
            self.chunk_contents = [self.chunk_contents[i] for i in indices_to_keep]
            self.chunk_metadata = [self.chunk_metadata[i] for i in indices_to_keep]
            self.tokenized_corpus = [self.tokenized_corpus[i] for i in indices_to_keep]
            self._rebuild()
            self._save()

    def reset(self) -> None:
        self.bm25 = None
        self.chunk_ids = []
        self.chunk_contents = []
        self.chunk_metadata = []
        self.tokenized_corpus = []
        if self.index_file.exists():
            self.index_file.unlink()

    def _tokenize(self, text: str) -> list[str]:
        return [token for token in re.findall(r"[a-z0-9][a-z0-9\-]+", text.lower()) if len(token) >= 2]

    def _rebuild(self) -> None:
        try:
            from rank_bm25 import BM25Okapi

            self.bm25 = BM25Okapi(self.tokenized_corpus) if self.tokenized_corpus else None
        except Exception:
            self.bm25 = None

    def _save(self) -> None:
        with self.index_file.open("wb") as handle:
            pickle.dump(
                {
                    "chunk_ids": self.chunk_ids,
                    "chunk_contents": self.chunk_contents,
                    "chunk_metadata": self.chunk_metadata,
                    "tokenized_corpus": self.tokenized_corpus,
                },
                handle,
            )

    def _load(self) -> None:
        if not self.index_file.exists():
            return
        try:
            with self.index_file.open("rb") as handle:
                data = pickle.load(handle)
            self.chunk_ids = data.get("chunk_ids", [])
            self.chunk_contents = data.get("chunk_contents", [])
            self.chunk_metadata = data.get("chunk_metadata", [])
            self.tokenized_corpus = data.get("tokenized_corpus", [])
            self._rebuild()
        except Exception:
            self.reset()

    def _matches_filters(self, metadata: dict, filters: dict) -> bool:
        for key, value in filters.items():
            if metadata.get(key) != value:
                return False
        return True
