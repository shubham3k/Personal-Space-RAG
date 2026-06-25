"""Local git activity connector placeholder."""

from src.integrations.base import BaseConnector, SyncResult


class GitConnector(BaseConnector):
    id = "git"
    name = "Git Activity"

    def sync(self) -> SyncResult:
        return SyncResult(self.id, "not_configured", errors=["Configure repository roots before syncing git activity."])
