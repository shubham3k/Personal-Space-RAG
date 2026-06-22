"""Hashing helpers."""

import hashlib
from pathlib import Path


def compute_file_hash(path: Path) -> str:
    digest = hashlib.md5()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def stable_id(*parts: object) -> str:
    text = "::".join(str(part) for part in parts)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
