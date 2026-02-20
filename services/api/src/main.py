"""Warranty Claim Audit API — FastAPI application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .routers import scoring

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Hybrid warranty claim auditing system with dual scoring engine",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(scoring.router)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.get("/status")
async def status() -> dict:
    return {
        "app": settings.app_name,
        "version": "0.1.0",
        "embedding_model": settings.embedding_model,
        "qdrant_host": settings.qdrant_host,
        "services": {
            "pii_redactor": "stub",
            "decomposer": "active",
            "embedder": "stub",
            "vector_scorer": "stub",
            "ml_scorer": "stub",
            "fusion": "active",
        },
    }
