# Personal Life OS

A privacy-first local RAG system for personal documents. Drop Markdown, text, PDF, JSON, or CSV files into `data/raw`, ingest them with local embeddings, and ask questions through FastAPI or Streamlit. LLM calls use free-tier providers in priority order: Groq, Cerebras, Gemini, then local Ollama.

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

## Main Commands

```bash
python scripts/setup_db.py
python scripts/seed_sample_data.py
python scripts/run_ingestion.py
uvicorn api.main:app --reload
streamlit run ui/app.py
pytest
```

## API

- `GET /health`
- `POST /ingest` with optional `{ "path": "data/raw/notes" }`
- `GET /documents`
- `POST /query` with `{ "query": "What do my notes say about local embeddings?", "top_k": 8 }`
- `GET /conversations/{conversation_id}`

## Privacy Model

Documents, chunks, embeddings, metadata, and conversation history stay local in `data/`. Only the user query and retrieved context snippets are sent to the selected LLM provider. Ollama can be used as the offline fallback when configured locally.
