"""JSON loader."""

import json
from pathlib import Path

from src.ingestion.loaders.base_loader import BaseLoader, LoadedDocument, LoaderError
from src.utils.hashing import compute_file_hash
from src.utils.text_processing import clean_text


class JSONLoader(BaseLoader):
    @property
    def supported_extensions(self) -> set[str]:
        return {".json"}

    def load(self, file_path: Path) -> LoadedDocument:
        try:
            data = json.loads(file_path.read_text(encoding=self._detect_encoding(file_path)))
        except Exception as exc:
            raise LoaderError(f"Could not parse JSON {file_path}: {exc}") from exc
        content = clean_text(json.dumps(data, indent=2, ensure_ascii=False))
        return LoadedDocument(
            content=content,
            metadata={"title": file_path.stem, "type": "json", "tags": []},
            source_path=str(file_path),
            file_type="json",
            file_hash=compute_file_hash(file_path),
            char_count=len(content),
            word_count=len(content.split()),
        )
