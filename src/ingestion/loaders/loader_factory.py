"""Loader selection by extension."""

from pathlib import Path

from src.ingestion.loaders import DEFAULT_LOADERS


class LoaderFactory:
    def __init__(self, loaders=None):
        self.loaders = loaders or DEFAULT_LOADERS

    def get_loader(self, path: Path):
        for loader in self.loaders:
            if loader.can_load(path):
                return loader
        raise ValueError(f"No loader for {path.suffix}")
