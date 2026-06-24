"""Audio metadata helpers."""

from pathlib import Path


def get_audio_duration_seconds(path: Path) -> float | None:
    try:
        from pydub import AudioSegment

        audio = AudioSegment.from_file(path)
        return len(audio) / 1000.0
    except Exception:
        return None


def audio_metadata(path: Path) -> dict:
    duration = get_audio_duration_seconds(path)
    return {"duration_seconds": duration, "extension": path.suffix.lower()}
