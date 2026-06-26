"""Plain text loader."""

from datetime import datetime
from pathlib import Path

from src.ingestion.loaders.base_loader import BaseLoader, LoadedDocument, LoaderError
from src.utils.date_parser import extract_date_from_filename
from src.utils.hashing import compute_file_hash
from src.utils.text_processing import clean_text


class TextLoader(BaseLoader):
    @property
    def supported_extensions(self) -> set[str]:
        return {".txt"}

    def load(self, file_path: Path) -> LoadedDocument:
        if not file_path.exists():
            raise FileNotFoundError(file_path)
        if self._is_binary(file_path):
            raise LoaderError(f"File appears binary: {file_path}")
        encoding = self._detect_encoding(file_path)
        try:
            content_raw = file_path.read_text(encoding=encoding)
        except Exception:
            content_raw = file_path.read_text(encoding=encoding, errors="replace")
        content = clean_text(content_raw)
        if not content:
            raise LoaderError(f"File has no content: {file_path}")
        date = extract_date_from_filename(file_path.name) or datetime.fromtimestamp(file_path.stat().st_mtime).strftime("%Y-%m-%d")
        return LoadedDocument(
            content=content,
            metadata={"title": file_path.stem.replace("_", " ").replace("-", " ").title(), "date": date, "tags": [], "type": "text"},
            source_path=str(file_path),
            file_type="text",
            file_hash=compute_file_hash(file_path),
            char_count=len(content),
            word_count=len(content.split()),
        )
