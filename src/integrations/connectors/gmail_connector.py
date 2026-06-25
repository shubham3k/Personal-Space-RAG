"""Gmail connector placeholder for OAuth-backed sync."""

from src.integrations.base import BaseConnector, SyncResult


class GmailConnector(BaseConnector):
    id = "gmail"
    name = "Gmail"
    supports_connect = True

    def sync(self) -> SyncResult:
        return SyncResult(self.id, "not_connected", errors=["Gmail OAuth is not configured yet."])
