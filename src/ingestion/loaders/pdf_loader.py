"""PDF text loader."""

from pathlib import Path

from src.ingestion.loaders.base_loader import BaseLoader, LoadedDocument, LoaderError
from src.ingestion.processors.table_extractor import TableExtractor
from src.utils.hashing import compute_file_hash
from src.utils.text_processing import clean_text


class PDFLoader(BaseLoader):
    def __init__(self):
        self.table_extractor = TableExtractor()

    @property
    def supported_extensions(self) -> set[str]:
        return {".pdf"}

    def load(self, file_path: Path) -> LoadedDocument:
        if not file_path.exists():
            raise FileNotFoundError(file_path)
        try:
            import fitz

            pages: list[str] = []
            page_count = 0
            with fitz.open(file_path) as doc:
                page_count = doc.page_count
                for page in doc:
                    pages.append(page.get_text())
            tables = self.table_extractor.extract_tables(file_path)
            content = clean_text("\n\n".join(pages + tables))
        except Exception as exc:
            raise LoaderError(f"Could not load PDF {file_path}: {exc}") from exc
        if not content:
            raise LoaderError(f"PDF has no extractable text: {file_path}")
        return LoadedDocument(
            content=content,
            metadata={"title": file_path.stem, "type": "pdf", "media_type": "pdf", "page_count": page_count, "tags": []},
            source_path=str(file_path),
            file_type="pdf",
            file_hash=compute_file_hash(file_path),
            char_count=len(content),
            word_count=len(content.split()),
        )
