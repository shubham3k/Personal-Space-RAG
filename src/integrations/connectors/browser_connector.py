"""Browser history/export connector placeholder."""

from src.integrations.base import BaseConnector, SyncResult


class BrowserConnector(BaseConnector):
    id = "browser"
    name = "Browser History"

    def sync(self) -> SyncResult:
        return SyncResult(self.id, "not_configured", errors=["Configure a browser export path before syncing."])
