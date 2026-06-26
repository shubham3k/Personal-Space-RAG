"""Markdown loader with frontmatter and tag extraction."""

import re
from datetime import datetime
from pathlib import Path

import frontmatter

from config.constants import DOC_TYPE_MAP
from src.ingestion.loaders.base_loader import BaseLoader, LoadedDocument, LoaderError
from src.utils.date_parser import extract_date_from_filename, extract_date_from_text
from src.utils.hashing import compute_file_hash
from src.utils.text_processing import clean_text


class MarkdownLoader(BaseLoader):
    @property
    def supported_extensions(self) -> set[str]:
        return {".md", ".markdown"}

    def load(self, file_path: Path) -> LoadedDocument:
        if not file_path.exists():
            raise FileNotFoundError(file_path)
        if self._is_binary(file_path):
            raise LoaderError(f"File appears binary: {file_path}")

        encoding = self._detect_encoding(file_path)
        try:
            raw_text = file_path.read_text(encoding=encoding)
        except Exception:
            raw_text = file_path.read_text(encoding=encoding, errors="replace")
        metadata: dict = {}
        content = raw_text
        try:
            post = frontmatter.loads(raw_text)
            metadata = dict(post.metadata or {})
            content = post.content
        except Exception:
            pass

        content = clean_text(content)
        if not content:
            raise LoaderError(f"File has no content: {file_path}")

        doc_metadata = self._extract_metadata(file_path, content, metadata)
        hashtags = set(re.findall(r"(?<!\w)#([\w-]+)", content))
        if hashtags:
            doc_metadata["tags"] = sorted(set(doc_metadata.get("tags", [])) | {t.lower() for t in hashtags})

        return LoadedDocument(
            content=content,
            metadata=doc_metadata,
            source_path=str(file_path),
            file_type="markdown",
            file_hash=compute_file_hash(file_path),
            char_count=len(content),
            word_count=len(content.split()),
        )

    def _extract_metadata(self, file_path: Path, content: str, fm_metadata: dict) -> dict:
        tags = fm_metadata.get("tags", [])
        if isinstance(tags, str):
            tags = [tag.strip() for tag in tags.split(",")]
        date = fm_metadata.get("date") or extract_date_from_filename(file_path.name) or extract_date_from_text(content[:500])
        if not date:
            date = datetime.fromtimestamp(file_path.stat().st_mtime).strftime("%Y-%m-%d")
        return {
            "title": fm_metadata.get("title") or self._title_from_content(content) or self._title_from_filename(file_path),
            "date": str(date),
            "tags": [str(tag).lower().strip() for tag in tags if str(tag).strip()],
            "type": self._detect_type_from_path(file_path),
        }

    def _title_from_content(self, content: str) -> str:
        match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        return match.group(1).strip() if match else ""

    def _title_from_filename(self, file_path: Path) -> str:
        name = re.sub(r"^\d{4}[-_]?\d{2}[-_]?\d{2}[-_]?", "", file_path.stem)
        return re.sub(r"[-_]+", " ", name).strip().title() or file_path.stem

    def _detect_type_from_path(self, file_path: Path) -> str:
        for part in file_path.parts:
            if part.lower() in DOC_TYPE_MAP:
                return DOC_TYPE_MAP[part.lower()]
        return "note"
