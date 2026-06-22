"""FastAPI exception handlers."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.generation.llm_client import AllProvidersFailedError


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(AllProvidersFailedError)
    async def all_providers_failed(_: Request, exc: AllProvidersFailedError):
        return JSONResponse(
            status_code=503,
            content={"detail": "No LLM provider is currently available.", "errors": exc.errors},
        )

    @app.exception_handler(ValueError)
    async def value_error(_: Request, exc: ValueError):
        return JSONResponse(status_code=400, content={"detail": str(exc)})
