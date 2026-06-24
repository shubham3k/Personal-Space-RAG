"""Local Whisper transcription."""

from pathlib import Path

from config.settings import settings
from src.utils.audio_utils import get_audio_duration_seconds


class AudioTranscriber:
    def __init__(self):
        self._model = None

    def transcribe(self, audio_path: Path) -> dict:
        duration = get_audio_duration_seconds(audio_path)
        max_seconds = settings.max_audio_duration_minutes * 60
        if duration is not None and duration > max_seconds:
            return {"text": "", "duration_seconds": duration, "error": "Audio exceeds configured maximum duration"}
        try:
            from faster_whisper import WhisperModel

            if self._model is None:
                self._model = WhisperModel(settings.whisper_model, device=settings.whisper_device)
            language = settings.whisper_language or None
            segments, info = self._model.transcribe(str(audio_path), language=language)
            text = " ".join(segment.text.strip() for segment in segments if segment.text.strip())
            return {"text": text, "duration_seconds": duration, "language": getattr(info, "language", language)}
        except Exception as exc:
            return {"text": "", "duration_seconds": duration, "error": str(exc)}
