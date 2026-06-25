"""RSS connector placeholder."""

from src.integrations.base import BaseConnector, SyncResult


class RSSConnector(BaseConnector):
    id = "rss"
    name = "RSS Feeds"

    def sync(self) -> SyncResult:
        return SyncResult(self.id, "not_configured", errors=["Configure feed URLs before syncing RSS."])
