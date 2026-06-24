"""Audio loader using local Whisper transcription."""

from pathlib import Path

from config.constants import SUPPORTED_AUDIO_EXTENSIONS
from config.settings import settings
from src.ingestion.loaders.base_loader import BaseLoader, LoadedDocument, LoaderError
from src.ingestion.processors.transcriber import AudioTranscriber
from src.utils.audio_utils import audio_metadata
from src.utils.hashing import compute_file_hash
from src.utils.text_processing import clean_text


class AudioLoader(BaseLoader):
    @property
    def supported_extensions(self) -> set[str]:
        return SUPPORTED_AUDIO_EXTENSIONS

    def __init__(self):
        self.transcriber = AudioTranscriber()

    def load(self, file_path: Path) -> LoadedDocument:
        if not file_path.exists():
            raise FileNotFoundError(file_path)
        metadata = audio_metadata(file_path)
        transcript = self.transcriber.transcribe(file_path)
        text = transcript.get("text", "")
        if text:
            transcript_path = Path(settings.transcripts_dir) / f"{file_path.stem}.txt"
            transcript_path.parent.mkdir(parents=True, exist_ok=True)
            transcript_path.write_text(text, encoding="utf-8")
            metadata["transcript_path"] = str(transcript_path)
        content = clean_text(f"Audio file: {file_path.name}\n\nTranscript:\n{text}")
        if not text:
            content = clean_text(f"Audio file: {file_path.name}\n\nTranscript unavailable.")
        if transcript.get("error"):
            metadata["transcription_error"] = transcript["error"]

        metadata.update(
            {
                "title": file_path.stem,
                "type": "audio",
                "media_type": "audio",
                "language": transcript.get("language", settings.whisper_language),
                "tags": [],
            }
        )
        if not content:
            raise LoaderError(f"Audio produced no searchable content: {file_path}")
        return LoadedDocument(
            content=content,
            metadata=metadata,
            source_path=str(file_path),
            file_type="audio",
            file_hash=compute_file_hash(file_path),
            char_count=len(content),
            word_count=len(content.split()),
        )
