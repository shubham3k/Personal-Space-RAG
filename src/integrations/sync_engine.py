"""Integration sync engine."""

from src.ingestion.pipeline import IngestionPipeline
from src.integrations.registry import available_connectors
from src.integrations.store import IntegrationStore


class IntegrationSyncEngine:
    def __init__(self):
        self.store = IntegrationStore()
        self.pipeline = IngestionPipeline()

    def sync(self, connector_id: str) -> dict:
        connectors = available_connectors()
        if connector_id not in connectors:
            raise ValueError(f"Unknown connector: {connector_id}")
        integration = self.store.get(connector_id) or {}
        connector = connectors[connector_id](integration.get("settings", {}))
        sync_id = self.store.start_sync(connector_id)
        result = connector.sync()
        self.store.set_status(connector_id, "connected" if result.status in {"ok", "partial"} else "disconnected")
        self.store.finish_sync(sync_id, result.status, result.items_processed, result.errors)
        return result.__dict__
