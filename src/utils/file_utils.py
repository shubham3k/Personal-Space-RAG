"""File helpers."""

import shutil
from pathlib import Path

from config.constants import MAX_FILE_SIZE_BYTES, SUPPORTED_EXTENSIONS


def is_supported_file(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS


def validate_file(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(path)
    if path.stat().st_size > MAX_FILE_SIZE_BYTES:
        raise ValueError(f"File exceeds configured size limit: {path}")
    if not is_supported_file(path):
        raise ValueError(f"Unsupported file type: {path.suffix}")


def check_disk_space(path: str = ".") -> int:
    return shutil.disk_usage(path).free
