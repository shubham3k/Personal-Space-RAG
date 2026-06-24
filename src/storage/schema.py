"""SQLite schema management for v3 tables."""

import sqlite3
from pathlib import Path

from config.settings import settings

EXPECTED_SCHEMA_VERSION = 3


class SchemaManager:
    def __init__(self, db_path: str | None = None):
        self.db_path = db_path or settings.sqlite_path
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

    def connect(self):
        return sqlite3.connect(self.db_path)

    def migrate(self) -> None:
        with self.connect() as conn:
            self._create_schema_version(conn)
            self._create_v3_tables(conn)
            conn.execute(
                """
                INSERT INTO schema_version (id, version, updated_at)
                VALUES (1, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(id) DO UPDATE SET version=excluded.version, updated_at=CURRENT_TIMESTAMP
                """,
                (EXPECTED_SCHEMA_VERSION,),
            )

    def _create_schema_version(self, conn: sqlite3.Connection) -> None:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS schema_version (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                version INTEGER NOT NULL,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

    def _create_v3_tables(self, conn: sqlite3.Connection) -> None:
        statements = [
            """
            CREATE TABLE IF NOT EXISTS integrations (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'disconnected',
                auth_token_encrypted TEXT,
                settings_json TEXT DEFAULT '{}',
                last_sync TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS sync_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                connector_id TEXT NOT NULL,
                start_time TEXT DEFAULT CURRENT_TIMESTAMP,
                end_time TEXT,
                items_processed INTEGER DEFAULT 0,
                status TEXT DEFAULT 'running',
                errors TEXT DEFAULT ''
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS entities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                type TEXT NOT NULL DEFAULT 'unknown',
                aliases TEXT DEFAULT '[]',
                first_seen TEXT DEFAULT CURRENT_TIMESTAMP,
                last_seen TEXT DEFAULT CURRENT_TIMESTAMP,
                mention_count INTEGER DEFAULT 0,
                UNIQUE(name, type)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS entity_mentions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_id INTEGER NOT NULL,
                document_id TEXT,
                mention_context TEXT,
                source_path TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS entity_relations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_a INTEGER NOT NULL,
                entity_b INTEGER NOT NULL,
                relation_type TEXT NOT NULL,
                strength REAL DEFAULT 0.0,
                evidence TEXT DEFAULT '',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,
                key TEXT NOT NULL,
                value TEXT NOT NULL,
                confidence REAL DEFAULT 1.0,
                source TEXT DEFAULT 'user',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(type, key)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS insights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,
                content TEXT NOT NULL,
                sources TEXT DEFAULT '[]',
                shown_to_user INTEGER DEFAULT 0,
                dismissed INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS digests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,
                period_start TEXT NOT NULL,
                period_end TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(type, period_start, period_end)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS scheduled_jobs (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                cron_expression TEXT NOT NULL,
                last_run TEXT,
                next_run TEXT,
                status TEXT DEFAULT 'idle',
                enabled INTEGER DEFAULT 1
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT,
                rating TEXT NOT NULL,
                comment TEXT DEFAULT '',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS daily_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                source TEXT NOT NULL,
                UNIQUE(date, metric_name, source)
            )
            """,
        ]
        for statement in statements:
            conn.execute(statement)
