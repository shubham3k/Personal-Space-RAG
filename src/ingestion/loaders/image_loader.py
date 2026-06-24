"""Image and screenshot loader with OCR and optional vision descriptions."""

from pathlib import Path

from config.constants import SUPPORTED_IMAGE_EXTENSIONS
from src.ingestion.loaders.base_loader import BaseLoader, LoadedDocument, LoaderError
from src.ingestion.processors.ocr_engine import OCREngine
from src.ingestion.processors.vision_describer import VisionDescriber
from src.utils.hashing import compute_file_hash
from src.utils.image_utils import create_thumbnail, perceptual_hash, validate_image
from src.utils.text_processing import clean_text


class ImageLoader(BaseLoader):
    @property
    def supported_extensions(self) -> set[str]:
        return SUPPORTED_IMAGE_EXTENSIONS

    def __init__(self):
        self.ocr = OCREngine()
        self.vision = VisionDescriber()

    def load(self, file_path: Path) -> LoadedDocument:
        if not file_path.exists():
            raise FileNotFoundError(file_path)
        try:
            image_info = validate_image(file_path)
            thumbnail_path = create_thumbnail(file_path)
        except Exception as exc:
            raise LoaderError(f"Could not load image {file_path}: {exc}") from exc

        ocr = self.ocr.extract_text(file_path)
        vision = self.vision.describe(file_path)
        sections = [f"Image file: {file_path.name}"]
        if ocr.get("text"):
            sections.append(f"OCR text:\n{ocr['text']}")
        if vision.get("description"):
            sections.append(f"Vision description:\n{vision['description']}")
        content = clean_text("\n\n".join(sections))

        metadata = {
            "title": file_path.stem,
            "type": "image",
            "media_type": "image",
            "thumbnail_path": thumbnail_path,
            "ocr_confidence": ocr.get("confidence", 0.0),
            "vision_provider": vision.get("provider", ""),
            "image_width": image_info.get("width"),
            "image_height": image_info.get("height"),
            "image_format": image_info.get("format"),
            "perceptual_hash": perceptual_hash(file_path),
            "tags": [],
        }
        if ocr.get("error"):
            metadata["ocr_error"] = ocr["error"]
        if vision.get("error"):
            metadata["vision_error"] = vision["error"]

        return LoadedDocument(
            content=content,
            metadata=metadata,
            source_path=str(file_path),
            file_type="image",
            file_hash=compute_file_hash(file_path),
            char_count=len(content),
            word_count=len(content.split()),
        )
