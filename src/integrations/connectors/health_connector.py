"""Health export connector placeholder."""

from src.integrations.base import BaseConnector, SyncResult


class HealthConnector(BaseConnector):
    id = "health"
    name = "Health Data"

    def sync(self) -> SyncResult:
        return SyncResult(self.id, "not_configured", errors=["Configure an Apple Health/Google Fit export path before syncing."])
