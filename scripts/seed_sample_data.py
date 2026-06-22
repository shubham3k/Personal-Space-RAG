"""Create a small sample note for first-run testing."""

from pathlib import Path


def main() -> None:
    path = Path("data/raw/notes/2026-06-22-sample-note.md")
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(
            """---
title: Sample Note
tags: [demo, personal-life-os]
---

# Sample Note

This is a local note for testing Personal Life OS ingestion and retrieval.
It mentions that local embeddings keep private documents on this machine.
""",
            encoding="utf-8",
        )
    print(path)


if __name__ == "__main__":
    main()
