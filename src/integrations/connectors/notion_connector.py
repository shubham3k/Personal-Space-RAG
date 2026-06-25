"""Notion connector placeholder."""

from src.integrations.base import BaseConnector, SyncResult


class NotionConnector(BaseConnector):
    id = "notion"
    name = "Notion"
    supports_connect = True

    def sync(self) -> SyncResult:
        return SyncResult(self.id, "not_connected", errors=["Set a Notion token and database/page settings before syncing."])
