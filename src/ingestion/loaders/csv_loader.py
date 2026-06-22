"""CSV loader."""

import csv
from pathlib import Path

from src.ingestion.loaders.base_loader import BaseLoader, LoadedDocument, LoaderError
from src.utils.hashing import compute_file_hash
from src.utils.text_processing import clean_text


class CSVLoader(BaseLoader):
    @property
    def supported_extensions(self) -> set[str]:
        return {".csv"}

    def load(self, file_path: Path) -> LoadedDocument:
        try:
            rows: list[str] = []
            with file_path.open("r", encoding=self._detect_encoding(file_path), newline="") as handle:
                reader = csv.DictReader(handle)
                if reader.fieldnames:
                    for idx, row in enumerate(reader, start=1):
                        rows.append(f"Row {idx}: " + "; ".join(f"{k}: {v}" for k, v in row.items()))
                else:
                    handle.seek(0)
                    rows = [", ".join(row) for row in csv.reader(handle)]
        except Exception as exc:
            raise LoaderError(f"Could not parse CSV {file_path}: {exc}") from exc
        content = clean_text("\n".join(rows))
        if not content:
            raise LoaderError(f"CSV has no content: {file_path}")
        return LoadedDocument(
            content=content,
            metadata={"title": file_path.stem, "type": "csv", "tags": []},
            source_path=str(file_path),
            file_type="csv",
            file_hash=compute_file_hash(file_path),
            char_count=len(content),
            word_count=len(content.split()),
        )
