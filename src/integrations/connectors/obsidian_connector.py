"""Obsidian vault connector."""

from pathlib import Path

from src.integrations.base import BaseConnector, SyncResult


class ObsidianConnector(BaseConnector):
    id = "obsidian"
    name = "Obsidian Vault"

    def sync(self) -> SyncResult:
        vault_path = self.settings.get("vault_path", "")
        if not vault_path or not Path(vault_path).exists():
            return SyncResult(self.id, "not_configured", errors=["Set settings.vault_path to your Obsidian vault."])
        from src.ingestion.pipeline import IngestionPipeline

        result = IngestionPipeline().ingest_directory(vault_path)
        return SyncResult(self.id, "ok" if not result["errors"] else "partial", result["ingested"] + result["skipped"], [str(err) for err in result["errors"]])
