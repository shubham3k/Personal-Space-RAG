"""Calendar connector placeholder for OAuth-backed sync."""

from src.integrations.base import BaseConnector, SyncResult


class CalendarConnector(BaseConnector):
    id = "calendar"
    name = "Calendar"
    supports_connect = True

    def sync(self) -> SyncResult:
        return SyncResult(self.id, "not_connected", errors=["Calendar OAuth is not configured yet."])
