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
            content_text = "\n\n".join(pages).strip()

            # Fallback to OCR if there's very little extractable text
            if len(content_text) < 100:
                try:
                    from src.ingestion.processors.ocr_engine import OCREngine
                    import tempfile
                    
                    ocr = OCREngine()
                    ocr_text_parts = []
                    with fitz.open(file_path) as doc:
                        for page in doc:
                            # Render page to image at 150 DPI
                            pix = page.get_pixmap(matrix=fitz.Matrix(150/72, 150/72))
                            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                                tmp_path = Path(tmp.name)
                            try:
                                pix.save(str(tmp_path))
                                ocr_res = ocr.extract_text(tmp_path)
                                if ocr_res.get("text"):
                                    ocr_text_parts.append(ocr_res["text"])
                            finally:
                                if tmp_path.exists():
                                    tmp_path.unlink()
                    if ocr_text_parts:
                        content_text = "\n\n".join(ocr_text_parts)
                except Exception:
                    pass

            tables = self.table_extractor.extract_tables(file_path)
            content = clean_text(content_text + "\n\n" + "\n\n".join(tables))
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
