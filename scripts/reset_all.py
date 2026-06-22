"""Reset local generated stores."""

import shutil
from pathlib import Path

from config.settings import settings


def main() -> None:
    for path in (settings.chroma_persist_dir, Path(settings.sqlite_path).parent, "data/cache", "data/processed"):
        target = Path(path)
        if target.exists():
            shutil.rmtree(target)
    settings.ensure_directories()
    print("Generated stores reset.")


if __name__ == "__main__":
    main()
