"""Embedding service using sentence-transformers.

Generates dense vector embeddings for each claim component
using a pre-loaded sentence-transformer model.
"""

import logging
from functools import lru_cache

from sentence_transformers import SentenceTransformer

from ..config import settings
from ..models.components import ClaimComponents

logger = logging.getLogger(__name__)

_model: SentenceTransformer | None = None


def get_model() -> SentenceTransformer:
    """Lazy-load the sentence-transformer model."""
    global _model
    if _model is None:
        logger.info(f"Loading embedding model: {settings.embedding_model}")
        _model = SentenceTransformer(settings.embedding_model)
        logger.info("Embedding model loaded")
    return _model


def embed_text(text: str) -> list[float]:
    """Embed a single text string."""
    model = get_model()
    embedding = model.encode(text, normalize_embeddings=True)
    return embedding.tolist()


def embed_components(components: ClaimComponents) -> dict[str, list[float]]:
    """Generate embeddings for each available claim component.

    Returns a dict mapping component name to its embedding vector.
    """
    model = get_model()
    embeddings: dict[str, list[float]] = {}

    texts_to_embed: list[tuple[str, str]] = []

    if components.symptom:
        texts_to_embed.append(("symptom", components.symptom.description))
    if components.diagnosis:
        texts_to_embed.append(("diagnosis", components.diagnosis.description))
    if components.parts and components.parts.parts:
        parts_text = ", ".join(p.name for p in components.parts.parts)
        texts_to_embed.append(("parts", parts_text))
    if components.labor and components.labor.description:
        texts_to_embed.append(("labor", components.labor.description))
    if components.verbatim:
        texts_to_embed.append(("verbatim", components.verbatim.text))

    if not texts_to_embed:
        return embeddings

    # Batch encode for efficiency
    names = [t[0] for t in texts_to_embed]
    texts = [t[1] for t in texts_to_embed]

    vecs = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)

    for name, vec in zip(names, vecs):
        embeddings[name] = vec.tolist()

    return embeddings
