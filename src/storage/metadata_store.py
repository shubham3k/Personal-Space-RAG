"""SQLite metadata store."""

import sqlite3
from pathlib import Path

from config.settings import settings
from src.ingestion.loaders.base_loader import LoadedDocument


class MetadataStore:
    def __init__(self, db_path: str | None = None):
        self.db_path = db_path or settings.sqlite_path
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_path TEXT UNIQUE NOT NULL,
                    file_hash TEXT UNIQUE NOT NULL,
                    title TEXT,
                    doc_type TEXT,
                    metadata_json TEXT,
                    char_count INTEGER,
                    word_count INTEGER,
                    chunk_count INTEGER,
                    ingested_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

    def has_file_hash(self, file_hash: str) -> bool:
        with self._connect() as conn:
            row = conn.execute("SELECT 1 FROM documents WHERE file_hash = ?", (file_hash,)).fetchone()
        return row is not None

    def upsert_document(self, document: LoadedDocument, chunk_count: int) -> None:
        import json

        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO documents
                    (source_path, file_hash, title, doc_type, metadata_json, char_count, word_count, chunk_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(source_path) DO UPDATE SET
                    file_hash=excluded.file_hash,
                    title=excluded.title,
                    doc_type=excluded.doc_type,
                    metadata_json=excluded.metadata_json,
                    char_count=excluded.char_count,
                    word_count=excluded.word_count,
                    chunk_count=excluded.chunk_count,
                    ingested_at=CURRENT_TIMESTAMP
                """,
                (
                    document.source_path,
                    document.file_hash,
                    document.metadata.get("title", ""),
                    document.metadata.get("type", document.file_type),
                    json.dumps(document.metadata, ensure_ascii=False, default=str),
                    document.char_count,
                    document.word_count,
                    chunk_count,
                ),
            )

    def delete_by_source_path(self, source_path: str) -> None:
        """Delete a document row by its source_path."""
        with self._connect() as conn:
            conn.execute("DELETE FROM documents WHERE source_path = ?", (source_path,))

    def list_documents(self) -> list[dict]:
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("SELECT * FROM documents ORDER BY ingested_at DESC").fetchall()
        return [dict(row) for row in rows]

    def count(self) -> int:
        with self._connect() as conn:
            row = conn.execute("SELECT COUNT(*) FROM documents").fetchone()
        return int(row[0])
