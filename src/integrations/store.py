"""Integration registry and sync log storage."""

from __future__ import annotations

import json

from src.integrations.registry import available_connectors
from src.storage.v3_store import V3Store


class IntegrationStore(V3Store):
    def ensure_registered(self) -> None:
        with self.connect() as conn:
            for connector_id, connector in available_connectors().items():
                conn.execute(
                    """
                    INSERT INTO integrations (id, name, status)
                    VALUES (?, ?, 'disconnected')
                    ON CONFLICT(id) DO UPDATE SET name=excluded.name
                    """,
                    (connector_id, connector.name),
                )

    def list(self) -> list[dict]:
        self.ensure_registered()
        rows = self.list_rows("integrations", "ORDER BY name")
        for row in rows:
            row["settings"] = json.loads(row.pop("settings_json") or "{}")
            row.pop("auth_token_encrypted", None)
        return rows

    def get(self, connector_id: str) -> dict | None:
        self.ensure_registered()
        rows = self.list_rows("integrations", "WHERE id = ?", (connector_id,))
        if not rows:
            return None
        row = rows[0]
        row["settings"] = json.loads(row.pop("settings_json") or "{}")
        row.pop("auth_token_encrypted", None)
        return row

    def update_settings(self, connector_id: str, settings: dict) -> dict:
        self.ensure_registered()
        with self.connect() as conn:
            conn.execute(
                "UPDATE integrations SET settings_json = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (json.dumps(settings), connector_id),
            )
        return self.get(connector_id) or {}

    def set_status(self, connector_id: str, status: str) -> None:
        with self.connect() as conn:
            conn.execute("UPDATE integrations SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (status, connector_id))

    def start_sync(self, connector_id: str) -> int:
        with self.connect() as conn:
            cursor = conn.execute("INSERT INTO sync_log (connector_id) VALUES (?)", (connector_id,))
            return int(cursor.lastrowid)

    def finish_sync(self, sync_id: int, status: str, items_processed: int, errors: list[str] | None = None) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                UPDATE sync_log
                SET end_time=CURRENT_TIMESTAMP, status=?, items_processed=?, errors=?
                WHERE id=?
                """,
                (status, items_processed, "\n".join(errors or []), sync_id),
            )

    def logs(self, connector_id: str | None = None) -> list[dict]:
        if connector_id:
            return self.list_rows("sync_log", "WHERE connector_id = ? ORDER BY start_time DESC LIMIT 50", (connector_id,))
        return self.list_rows("sync_log", "ORDER BY start_time DESC LIMIT 50")
