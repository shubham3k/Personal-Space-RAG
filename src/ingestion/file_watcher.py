"""Watch data/raw and ingest changed files."""

import logging
from pathlib import Path
from threading import Timer

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from watchdog.observers.polling import PollingObserver

from config.constants import WATCH_IGNORE_PATTERNS, WATCH_IGNORE_PREFIXES
from config.settings import settings
from src.ingestion.pipeline import IngestionPipeline
from src.utils.file_utils import is_supported_file

logger = logging.getLogger(__name__)


class IngestionEventHandler(FileSystemEventHandler):
    def __init__(self, pipeline: IngestionPipeline):
        self.pipeline = pipeline
        self._timers: dict[str, Timer] = {}

    def on_created(self, event):
        if not event.is_directory:
            logger.info(f"[WATCHER] File created: {event.src_path}")
            self._schedule(event.src_path)

    def on_modified(self, event):
        if not event.is_directory:
            logger.info(f"[WATCHER] File modified: {event.src_path}")
            self._schedule(event.src_path)

    def _schedule(self, raw_path: str) -> None:
        path = Path(raw_path).resolve()
        if path.is_dir() or not is_supported_file(path) or self._ignored(path):
            return
        key = str(path)
        if key in self._timers:
            self._timers[key].cancel()
        timer = Timer(settings.watch_debounce_seconds, lambda: self._safe_ingest(path))
        self._timers[key] = timer
        timer.start()

    def _safe_ingest(self, path: Path) -> None:
        try:
            logger.info(f"[WATCHER] Debounce complete. Ingesting: {path}")
            self.pipeline.ingest_file(path)
        except Exception as exc:
            logger.error(f"[WATCHER] Ingestion failed for {path}: {exc}")

    def _ignored(self, path: Path) -> bool:
        return path.name in WATCH_IGNORE_PATTERNS or any(path.name.startswith(prefix) for prefix in WATCH_IGNORE_PREFIXES)


def start_watcher(directory: str | None = None) -> Observer | PollingObserver:
    pipeline = IngestionPipeline()
    watch_path = Path(directory or settings.watch_directory).resolve()
    watch_path.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"[WATCHER] Starting watcher on: {watch_path}")
    
    try:
        observer = Observer()
        observer.schedule(IngestionEventHandler(pipeline), str(watch_path), recursive=True)
        observer.start()
        logger.info("[WATCHER] Native observer started successfully.")
        return observer
    except Exception as e:
        logger.warning(f"[WATCHER] Native observer failed: {e}. Falling back to polling observer.")
        observer = PollingObserver(timeout=settings.watch_debounce_seconds or 2)
        observer.schedule(IngestionEventHandler(pipeline), str(watch_path), recursive=True)
        observer.start()
        logger.info("[WATCHER] Polling observer started successfully.")
        return observer
