.PHONY: install api ui ingest test lint seed setup upgrade

install:
	python -m pip install -r requirements.txt

upgrade: install setup ingest

setup:
	python scripts/setup_db.py

seed:
	python scripts/seed_sample_data.py

api:
	uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

ui:
	npm run --prefix web-ui dev

ingest:
	python scripts/run_ingestion.py

test:
	pytest

lint:
	ruff check .
