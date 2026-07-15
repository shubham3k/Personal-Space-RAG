# Personal Life OS

A privacy-first local RAG system for personal documents and media. Drop Markdown, text, PDF, JSON, CSV, images, screenshots, or audio into `data/raw`, ingest them with local embeddings plus BM25 keyword search, and ask questions through FastAPI or Streamlit. LLM calls use free-tier providers in priority order: Groq, Cerebras, Gemini, then local Ollama.

## Quick Start

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
copy .env.example .env
python scripts/setup_db.py
python scripts/seed_sample_data.py
python scripts/run_ingestion.py
uvicorn api.main:app --reload
```

In another terminal:

```bash
streamlit run ui/app.py
```

Open the API at `http://localhost:8000/docs` and the UI at `http://localhost:8501`.

## Configuration

Set at least one cloud provider key in `.env`, or install Ollama and pull the configured model:

```bash
ollama pull llama3.1:8b
ollama serve
```

Embeddings are always local through `sentence-transformers` using `all-MiniLM-L6-v2` by default.

## v2.0 Upgrade Notes

v2.0 adds hybrid search, reranking, query caching, rate limiting, image OCR/vision descriptions, audio transcription, PDF table extraction, media previews, and a lightweight evaluation page.

v3.0 adds an agentic routing layer, memory, insights, digests, entity and integration registries, timeline/correlation endpoints, and Streamlit pages for managing those systems. See `V3_UPGRADE_NOTES.txt`.

After pulling or applying the v2.0 changes, run:

```bash
python -m pip install -r requirements.txt
python scripts/setup_db.py
python scripts/run_ingestion.py
```

Re-running ingestion is important. Existing v1 documents are skipped for vector duplication, but their chunks are backfilled into the new BM25 index.

Optional local system dependencies:

- `ffmpeg` for broad audio decoding through pydub/faster-whisper
- Ghostscript for Camelot PDF table extraction
- Tesseract only if you switch `OCR_ENGINE=tesseract`

## Main Commands

```bash
python scripts/setup_db.py
python scripts/seed_sample_data.py
python scripts/run_ingestion.py
uvicorn api.main:app --reload
streamlit run ui/app.py
pytest
```

## Supported Files

- Text: `.md`, `.markdown`, `.txt`, `.pdf`, `.json`, `.csv`
- Images: `.png`, `.jpg`, `.jpeg`, `.webp`, `.gif`, `.bmp`, `.tiff`
- Audio: `.mp3`, `.wav`, `.m4a`, `.ogg`, `.flac`, `.wma`, `.aac`

## API

- `GET /health`
- `POST /ingest` with optional `{ "path": "data/raw/notes" }`
- `GET /documents`
- `POST /query` with `{ "query": "What do my notes say about local embeddings?", "top_k": 8 }`
- `GET /conversations/{conversation_id}`

## Privacy Model

Documents, chunks, embeddings, metadata, and conversation history stay local in `data/`. Only the user query and retrieved context snippets are sent to the selected LLM provider. Ollama can be used as the offline fallback when configured locally.
