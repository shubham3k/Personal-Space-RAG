"""Lightweight scheduled job registry for v3."""

from config.settings import settings
from src.storage.v3_store import V3Store


class JobStore(V3Store):
    def ensure_defaults(self) -> None:
        defaults = [
            ("daily_digest", "Daily Digest", settings.digest_daily_cron),
            ("weekly_review", "Weekly Review", settings.digest_weekly_cron),
            ("integration_sync", "Integration Sync", settings.integration_sync_cron),
        ]
        with self.connect() as conn:
            for job_id, name, cron in defaults:
                conn.execute(
                    """
                    INSERT INTO scheduled_jobs (id, name, cron_expression)
                    VALUES (?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET name=excluded.name, cron_expression=excluded.cron_expression
                    """,
                    (job_id, name, cron),
                )

    def list(self) -> list[dict]:
        self.ensure_defaults()
        return self.list_rows("scheduled_jobs", "ORDER BY name")
