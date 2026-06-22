"""Watch data/raw and ingest changed files."""

from pathlib import Path
from threading import Timer

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from config.constants import WATCH_IGNORE_PATTERNS, WATCH_IGNORE_PREFIXES
from config.settings import settings
from src.ingestion.pipeline import IngestionPipeline
from src.utils.file_utils import is_supported_file


class IngestionEventHandler(FileSystemEventHandler):
    def __init__(self, pipeline: IngestionPipeline):
        self.pipeline = pipeline
        self._timers: dict[str, Timer] = {}

    def on_created(self, event):
        self._schedule(event.src_path)

    def on_modified(self, event):
        self._schedule(event.src_path)

    def _schedule(self, raw_path: str) -> None:
        path = Path(raw_path)
        if path.is_dir() or not is_supported_file(path) or self._ignored(path):
            return
        key = str(path)
        if key in self._timers:
            self._timers[key].cancel()
        timer = Timer(settings.watch_debounce_seconds, lambda: self.pipeline.ingest_file(path))
        self._timers[key] = timer
        timer.start()

    def _ignored(self, path: Path) -> bool:
        return path.name in WATCH_IGNORE_PATTERNS or any(path.name.startswith(prefix) for prefix in WATCH_IGNORE_PREFIXES)


def start_watcher(directory: str | None = None) -> Observer:
    pipeline = IngestionPipeline()
    observer = Observer()
    observer.schedule(IngestionEventHandler(pipeline), directory or settings.watch_directory, recursive=True)
    observer.start()
    return observer
