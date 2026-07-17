import os
import tempfile
from pathlib import Path

from src.storage.bm25_store import BM25Store
from src.ingestion.chunker import DocumentChunk


def test_bm25_store_delete_by_source_path():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Initialize store on a temp directory
        store = BM25Store(persist_path=tmpdir)
        
        # Add chunks for documents
        chunk1 = DocumentChunk(
            id="doc1_chunk0",
            content="This is first chunk of document one.",
            metadata={"source_path": "doc1.md", "chunk_index": 0},
            source_path="doc1.md",
            chunk_index=0
        )
        chunk2 = DocumentChunk(
            id="doc2_chunk0",
            content="This is second document chunk content.",
            metadata={"source_path": "doc2.md", "chunk_index": 0},
            source_path="doc2.md",
            chunk_index=0
        )
        chunk3 = DocumentChunk(
            id="doc3_chunk0",
            content="Completely unrelated words here.",
            metadata={"source_path": "doc3.md", "chunk_index": 0},
            source_path="doc3.md",
            chunk_index=0
        )
        chunk4 = DocumentChunk(
            id="doc4_chunk0",
            content="Another distinct document corpus text.",
            metadata={"source_path": "doc4.md", "chunk_index": 0},
            source_path="doc4.md",
            chunk_index=0
        )
        
        store.add_chunks([chunk1, chunk2, chunk3, chunk4])
        assert store.count() == 4
        
        # Delete first document
        store.delete_by_source_path("doc1.md")
        assert store.count() == 3
        assert "doc1_chunk0" not in store.chunk_ids
        
        # Verify that searching for doc1 content never returns doc1_chunk0
        results = store.search("first chunk", top_k=5)
        for r in results:
            assert r["id"] != "doc1_chunk0"
        
        # Verify that searching for doc2 content returns it as top result
        results = store.search("second document", top_k=5)
        assert len(results) >= 1
        assert results[0]["id"] == "doc2_chunk0"
