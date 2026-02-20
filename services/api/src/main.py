"""Warranty Claim Audit API — FastAPI application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .routers import scoring

app = FastAPI(
    title=settings.app_name,
    version="0.2.0",
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
    # Check Qdrant connectivity
    qdrant_status = "unreachable"
    try:
        from qdrant_client import QdrantClient
        qc = QdrantClient(host=settings.qdrant_host, port=settings.qdrant_port, timeout=3)
        info = qc.get_collection("claim_components")
        qdrant_status = f"ok ({info.points_count} vectors)"
    except Exception:
        pass

    # Check ML model availability
    from pathlib import Path
    model_path = Path(settings.model_dir) / "model_calibrated.joblib"
    ml_status = "active" if model_path.exists() else "fallback (heuristic)"

    return {
        "app": settings.app_name,
        "version": "0.2.0",
        "embedding_model": settings.embedding_model,
        "qdrant_host": settings.qdrant_host,
        "services": {
            "pii_redactor": "stub (disabled)",
            "decomposer": "active",
            "embedder": "active",
            "vector_scorer": "active",
            "ml_scorer": ml_status,
            "fusion": "active",
            "qdrant": qdrant_status,
        },
    }
