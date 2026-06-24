"""Stores for v3 agentic and integration data."""

import json
import sqlite3
from pathlib import Path

from config.settings import settings
from src.storage.schema import SchemaManager


class V3Store:
    def __init__(self, db_path: str | None = None):
        self.db_path = db_path or settings.sqlite_path
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        SchemaManager(self.db_path).migrate()

    def connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def list_rows(self, table: str, where: str = "", params: tuple = ()) -> list[dict]:
        query = f"SELECT * FROM {table} {where}"
        with self.connect() as conn:
            return [dict(row) for row in conn.execute(query, params).fetchall()]


class MemoryStore(V3Store):
    def add(self, memory_type: str, key: str, value: str, confidence: float = 1.0, source: str = "user") -> dict:
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO memories (type, key, value, confidence, source)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(type, key) DO UPDATE SET
                    value=excluded.value,
                    confidence=excluded.confidence,
                    source=excluded.source,
                    updated_at=CURRENT_TIMESTAMP
                """,
                (memory_type, key, value, confidence, source),
            )
        return {"type": memory_type, "key": key, "value": value, "confidence": confidence, "source": source}

    def list(self) -> list[dict]:
        return self.list_rows("memories", "ORDER BY updated_at DESC")

    def delete(self, memory_id: int) -> None:
        with self.connect() as conn:
            conn.execute("DELETE FROM memories WHERE id = ?", (memory_id,))


class InsightStore(V3Store):
    def add(self, insight_type: str, content: str, sources: list | None = None) -> dict:
        with self.connect() as conn:
            cursor = conn.execute(
                "INSERT INTO insights (type, content, sources) VALUES (?, ?, ?)",
                (insight_type, content, json.dumps(sources or [])),
            )
            insight_id = cursor.lastrowid
        return {"id": insight_id, "type": insight_type, "content": content, "sources": sources or []}

    def pending(self) -> list[dict]:
        rows = self.list_rows("insights", "WHERE dismissed = 0 ORDER BY created_at DESC")
        for row in rows:
            row["sources"] = json.loads(row.get("sources") or "[]")
        return rows

    def dismiss(self, insight_id: int) -> None:
        with self.connect() as conn:
            conn.execute("UPDATE insights SET dismissed = 1 WHERE id = ?", (insight_id,))


class DigestStore(V3Store):
    def upsert(self, digest_type: str, period_start: str, period_end: str, content: str) -> dict:
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO digests (type, period_start, period_end, content)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(type, period_start, period_end) DO UPDATE SET
                    content=excluded.content,
                    created_at=CURRENT_TIMESTAMP
                """,
                (digest_type, period_start, period_end, content),
            )
        return {"type": digest_type, "period_start": period_start, "period_end": period_end, "content": content}

    def get(self, digest_type: str, date: str) -> dict | None:
        rows = self.list_rows("digests", "WHERE type = ? AND period_start <= ? AND period_end >= ? ORDER BY created_at DESC LIMIT 1", (digest_type, date, date))
        return rows[0] if rows else None

    def list(self) -> list[dict]:
        return self.list_rows("digests", "ORDER BY created_at DESC")


class EntityStore(V3Store):
    def upsert(self, name: str, entity_type: str = "unknown", aliases: list[str] | None = None) -> dict:
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO entities (name, type, aliases, mention_count)
                VALUES (?, ?, ?, 1)
                ON CONFLICT(name, type) DO UPDATE SET
                    aliases=excluded.aliases,
                    mention_count=mention_count + 1,
                    last_seen=CURRENT_TIMESTAMP
                """,
                (name, entity_type, json.dumps(aliases or [])),
            )
            row = conn.execute("SELECT * FROM entities WHERE name = ? AND type = ?", (name, entity_type)).fetchone()
        return dict(row)

    def list(self) -> list[dict]:
        rows = self.list_rows("entities", "ORDER BY mention_count DESC, last_seen DESC")
        for row in rows:
            row["aliases"] = json.loads(row.get("aliases") or "[]")
        return rows

    def get(self, entity_id: int) -> dict | None:
        rows = self.list_rows("entities", "WHERE id = ?", (entity_id,))
        if not rows:
            return None
        entity = rows[0]
        entity["aliases"] = json.loads(entity.get("aliases") or "[]")
        entity["mentions"] = self.list_rows("entity_mentions", "WHERE entity_id = ? ORDER BY created_at DESC LIMIT 25", (entity_id,))
        return entity


class FeedbackStore(V3Store):
    def add(self, conversation_id: str | None, rating: str, comment: str = "") -> dict:
        with self.connect() as conn:
            cursor = conn.execute(
                "INSERT INTO feedback (conversation_id, rating, comment) VALUES (?, ?, ?)",
                (conversation_id, rating, comment),
            )
        return {"id": cursor.lastrowid, "conversation_id": conversation_id, "rating": rating, "comment": comment}

    def stats(self) -> dict:
        rows = self.list_rows("feedback")
        return {
            "total": len(rows),
            "good": sum(1 for row in rows if row["rating"] == "good"),
            "bad": sum(1 for row in rows if row["rating"] == "bad"),
        }


class DailyMetricStore(V3Store):
    def upsert(self, date: str, metric_name: str, metric_value: float, source: str) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO daily_metrics (date, metric_name, metric_value, source)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(date, metric_name, source) DO UPDATE SET metric_value=excluded.metric_value
                """,
                (date, metric_name, metric_value, source),
            )

    def list(self) -> list[dict]:
        return self.list_rows("daily_metrics", "ORDER BY date DESC")
