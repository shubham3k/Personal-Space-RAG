from src.ingestion.chunker import TextChunker
from src.ingestion.loaders.base_loader import LoadedDocument


def test_chunker_preserves_metadata():
    document = LoadedDocument(
        content="First paragraph.\n\nSecond paragraph with more text.",
        metadata={"title": "Test", "type": "note"},
        source_path="note.md",
        file_hash="abc",
        file_type="markdown",
    )

    chunks = TextChunker(chunk_size=100, chunk_overlap=10, min_chunk_size=1).chunk(document)

    assert chunks
    assert chunks[0].metadata["title"] == "Test"
    assert chunks[0].source_path == "note.md"
