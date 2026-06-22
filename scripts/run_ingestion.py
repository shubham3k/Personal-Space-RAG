"""Run ingestion for a file or directory."""

from pathlib import Path
import sys
import argparse

# Ensure project root is on sys.path so top-level imports like `config` resolve
# when running the script directly (e.g. `python scripts/run_ingestion.py`).
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config.settings import settings
from src.ingestion.pipeline import IngestionPipeline


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs="?", default=settings.raw_data_dir)
    parser.add_argument("--force", "-f", action="store_true", help="Force re-ingest by removing existing metadata entries for the target files before ingestion")
    args = parser.parse_args()
    pipeline = IngestionPipeline()
    path = Path(args.path)

    if args.force:
        # Remove metadata rows for the target files so ingestion will run again.
        from src.storage.metadata_store import MetadataStore

        m = MetadataStore()
        if path.is_dir():
            for p in path.rglob("*"):
                if p.is_file():
                    m.delete_by_source_path(str(p))
        else:
            m.delete_by_source_path(str(path))

    print(pipeline.ingest_directory(path) if path.is_dir() else pipeline.ingest_file(path))


if __name__ == "__main__":
    main()
