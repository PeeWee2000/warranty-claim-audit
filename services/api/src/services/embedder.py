"""Embedding service — stub.

Will generate vector embeddings for each claim component using
sentence-transformers (e.g., all-MiniLM-L6-v2).
"""

from ..models.components import ClaimComponents


def embed_components(components: ClaimComponents) -> dict[str, list[float]]:
    """Placeholder: returns empty embeddings.

    A real implementation would load a sentence-transformer model
    and produce dense vectors for each textual component.
    """
    return {name: [] for name in components.available_components}
