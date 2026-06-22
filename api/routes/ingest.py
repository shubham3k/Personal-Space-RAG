"""Ingestion endpoints."""

from pathlib import Path

from fastapi import APIRouter

from api.schemas.request import IngestRequest
from config.settings import settings
from src.ingestion.pipeline import IngestionPipeline

router = APIRouter(prefix="/ingest", tags=["ingest"])
pipeline = IngestionPipeline()


@router.post("")
def ingest(request: IngestRequest):
    path = Path(request.path or settings.raw_data_dir)
    if path.is_dir():
        return pipeline.ingest_directory(path)
    return pipeline.ingest_file(path)
