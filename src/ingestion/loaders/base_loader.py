"""Base document loader interface and data models."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


@dataclass
class LoadedDocument:
    content: str
    metadata: dict = field(default_factory=dict)
    source_path: str = ""
    file_type: str = ""
    file_hash: str = ""
    char_count: int = 0
    word_count: int = 0
    load_timestamp: datetime = field(default_factory=datetime.now)


class LoaderError(Exception):
    """Raised when a document cannot be loaded."""


class BaseLoader(ABC):
    @property
    @abstractmethod
    def supported_extensions(self) -> set[str]:
        raise NotImplementedError

    @abstractmethod
    def load(self, file_path: Path) -> LoadedDocument:
        raise NotImplementedError

    def can_load(self, file_path: Path) -> bool:
        return file_path.suffix.lower() in self.supported_extensions

    def _detect_encoding(self, file_path: Path) -> str:
        for encoding in ("utf-8", "utf-8-sig", "latin-1", "cp1252"):
            try:
                file_path.read_text(encoding=encoding)
                return encoding
            except (UnicodeDecodeError, ValueError):
                continue
        return "utf-8"

    def _is_binary(self, file_path: Path) -> bool:
        chunk = file_path.read_bytes()[:8192]
        if b"\x00" in chunk:
            return True
        if not chunk:
            return False
        non_text = sum(1 for b in chunk if b < 8 or (b > 13 and b < 32))
        return non_text / len(chunk) > 0.3
