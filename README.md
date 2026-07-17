# Personal Life OS

Personal Life OS is a privacy-first local RAG project for searching and querying your own documents, notes, PDFs, images, and audio.

Instead of sending your personal data to a public cloud service, the project keeps documents and embeddings locally and uses a hosted LLM provider only when needed.

## What this project does

- Ingests personal files from `data/raw`
- Builds local vector search and keyword search
- Answers questions through a FastAPI backend
- Supports multimodal data such as text, PDFs, images, and audio
- Keeps the main knowledge index and metadata local in the workspace

## Minimal setup

### 1. Create and activate a virtual environment

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 2. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 3. Configure environment variables

```bash
copy .env.example .env
```

Update `.env` with at least one LLM provider key, or use Ollama locally.

### 4. Initialize the local database

```bash
python scripts/setup_db.py
```

### 5. Add your documents

Place files in folders like:

- `data/raw/notes`
- `data/raw/pdfs`
- `data/raw/images`
- `data/raw/audio`

### 6. Run ingestion

```bash
python scripts/run_ingestion.py
```

### 7. Start the API

```bash
uvicorn api.main:app --reload
```

Then open:

- API docs: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`

## Basic usage

You can query the project through the API:

```bash
POST /query
{
  "query": "What do my notes say about personal knowledge?",
  "top_k": 8
}
```

Or use the ingestion endpoint to add content from a folder.

## Project structure

- `api/` — FastAPI routes and server
- `src/` — retrieval, orchestration, agents, and generation logic
- `data/raw/` — source documents and media
- `data/chroma_db/` — vector database storage
- `data/sqlite/` — local metadata database
- `scripts/` — setup, ingestion, and sample-data utilities

## Notes

- The default embedding model is local and runs through `sentence-transformers`.
- The app can fall back to `Ollama` for offline local inference.
- The repository also includes a frontend web folder under `web-ui/` for UI work.

## Common commands

```bash
python scripts/setup_db.py
python scripts/run_ingestion.py
uvicorn api.main:app --reload
pytest
```

## Privacy model

Your files, chunks, embeddings, and metadata stay local in the project workspace. Only the query text and selected retrieval context are sent to the configured LLM provider.
