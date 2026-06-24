"""OCR engines for images and screenshots."""

from pathlib import Path

from config.settings import settings


class OCREngine:
    def __init__(self, engine: str | None = None):
        self.engine = (engine or settings.ocr_engine).lower()
        self._reader = None

    def extract_text(self, image_path: Path) -> dict:
        try:
            if self.engine == "tesseract":
                return self._extract_tesseract(image_path)
            return self._extract_easyocr(image_path)
        except Exception as exc:
            return {"text": "", "confidence": 0.0, "error": str(exc)}

    def _extract_easyocr(self, image_path: Path) -> dict:
        import easyocr

        if self._reader is None:
            languages = [lang.strip() for lang in settings.ocr_languages.split(",") if lang.strip()]
            self._reader = easyocr.Reader(languages or ["en"], gpu=settings.ocr_gpu)
        results = self._reader.readtext(str(image_path))
        accepted = []
        confidences = []
        for _, text, confidence in results:
            if confidence >= settings.ocr_confidence_threshold:
                accepted.append(text)
                confidences.append(float(confidence))
        return {"text": "\n".join(accepted), "confidence": sum(confidences) / len(confidences) if confidences else 0.0}

    def _extract_tesseract(self, image_path: Path) -> dict:
        import pytesseract
        from PIL import Image

        with Image.open(image_path) as image:
            text = pytesseract.image_to_string(image)
        return {"text": text.strip(), "confidence": 1.0 if text.strip() else 0.0}
