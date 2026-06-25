"""WhatsApp export connector placeholder."""

from src.integrations.base import BaseConnector, SyncResult


class WhatsAppConnector(BaseConnector):
    id = "whatsapp"
    name = "WhatsApp Export"

    def sync(self) -> SyncResult:
        return SyncResult(self.id, "not_configured", errors=["Configure a WhatsApp export file or folder before syncing."])
