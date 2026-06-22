"""FastAPI entrypoint."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.middleware.error_handler import register_error_handlers
from api.routes import conversations, documents, health, ingest, query
from config.logging_config import configure_logging
from config.settings import settings
from src.utils.file_utils import check_disk_space

configure_logging()

app = FastAPI(title="Personal Life OS", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
register_error_handlers(app)

app.include_router(health.router)
app.include_router(query.router)
app.include_router(ingest.router)
app.include_router(documents.router)
app.include_router(conversations.router)


@app.on_event("startup")
async def startup() -> None:
    settings.ensure_directories()
    if check_disk_space(".") < 1024 * 1024 * 1024:
        import structlog

        structlog.get_logger().warning("Low disk space: less than 1GB available")


@app.get("/")
def root():
    return {"name": "Personal Life OS", "status": "ready"}
