"""Document chunking."""

from dataclasses import dataclass, field

from config.settings import settings
from src.ingestion.loaders.base_loader import LoadedDocument
from src.utils.hashing import stable_id


@dataclass
class DocumentChunk:
    id: str
    content: str
    metadata: dict = field(default_factory=dict)
    source_path: str = ""
    chunk_index: int = 0


class TextChunker:
    def __init__(self, chunk_size: int | None = None, chunk_overlap: int | None = None, min_chunk_size: int | None = None):
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = chunk_overlap if chunk_overlap is not None else settings.chunk_overlap
        self.min_chunk_size = min_chunk_size or settings.min_chunk_size

    def chunk(self, document: LoadedDocument) -> list[DocumentChunk]:
        paragraphs = self._sections(document.content) if document.file_type == "markdown" else [p.strip() for p in document.content.split("\n\n") if p.strip()]
        chunks: list[str] = []
        current = ""
        for paragraph in paragraphs:
            if len(current) + len(paragraph) + 2 <= self.chunk_size:
                current = f"{current}\n\n{paragraph}".strip()
            else:
                if current:
                    chunks.extend(self._split_long(current))
                current = paragraph
        if current:
            chunks.extend(self._split_long(current))
        return [
            DocumentChunk(
                id=stable_id(document.file_hash, index, text[:80]),
                content=text,
                metadata={**document.metadata, "file_hash": document.file_hash, "file_type": document.file_type},
                source_path=document.source_path,
                chunk_index=index,
            )
            for index, text in enumerate(chunks)
            if len(text.strip()) >= self.min_chunk_size
        ]

    def _split_long(self, text: str) -> list[str]:
        if len(text) <= self.chunk_size:
            return [text]
        chunks = []
        step = max(1, self.chunk_size - self.chunk_overlap)
        for start in range(0, len(text), step):
            chunk = text[start : start + self.chunk_size].strip()
            if chunk:
                chunks.append(chunk)
        return chunks

    def _sections(self, text: str) -> list[str]:
        sections: list[str] = []
        current: list[str] = []
        for line in text.splitlines():
            if line.startswith("#") and current:
                sections.append("\n".join(current).strip())
                current = [line]
            else:
                current.append(line)
        if current:
            sections.append("\n".join(current).strip())
        refined: list[str] = []
        for section in sections:
            if len(section) <= self.chunk_size:
                refined.append(section)
            else:
                refined.extend([p.strip() for p in section.split("\n\n") if p.strip()])
        return refined
