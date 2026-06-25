"""Base connector contracts."""

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class SyncDocument:
    title: str
    content: str
    source: str
    external_id: str
    metadata: dict = field(default_factory=dict)


@dataclass
class SyncResult:
    connector_id: str
    status: str
    items_processed: int = 0
    errors: list[str] = field(default_factory=list)


class BaseConnector:
    id = "base"
    name = "Base Connector"
    supports_connect = False

    def __init__(self, settings: dict | None = None):
        self.settings = settings or {}

    def status(self) -> dict:
        return {"id": self.id, "name": self.name, "status": "available", "supports_connect": self.supports_connect}

    def sync(self) -> SyncResult:
        return SyncResult(self.id, "not_implemented", errors=["Connector does not implement sync"])

    def _read_text_files(self, root: str, suffixes: set[str]) -> list[Path]:
        path = Path(root)
        if not path.exists():
            return []
        return [item for item in path.rglob("*") if item.is_file() and item.suffix.lower() in suffixes]
