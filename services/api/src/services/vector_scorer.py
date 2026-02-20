"""Vector similarity scoring service using Qdrant.

Queries the vector database with per-component embeddings to find
similar historical claims, then derives consistency/anomaly scores
based on what outcomes those similar claims had.
"""

import logging

from qdrant_client import QdrantClient
from qdrant_client.models import ScoredPoint

from ..config import settings
from ..models.scoring import ComponentScore, ConcernLevel, ScoreBreakdown

logger = logging.getLogger(__name__)

_client: QdrantClient | None = None

COLLECTION_NAME = "claim_components"
TOP_K = 10


def get_client() -> QdrantClient:
    """Lazy-initialize Qdrant client."""
    global _client
    if _client is None:
        _client = QdrantClient(
            host=settings.qdrant_host,
            port=settings.qdrant_port,
        )
        logger.info(f"Connected to Qdrant at {settings.qdrant_host}:{settings.qdrant_port}")
    return _client


def _concern_from_score(s: float) -> ConcernLevel:
    """Map a 0-1 score to a concern level."""
    if s >= 0.75:
        return ConcernLevel.NORMAL
    elif s >= 0.55:
        return ConcernLevel.LOW_CONCERN
    elif s >= 0.35:
        return ConcernLevel.MODERATE_CONCERN
    else:
        return ConcernLevel.HIGH_CONCERN


def _score_component(
    client: QdrantClient,
    component_name: str,
    embedding: list[float],
) -> ComponentScore:
    """Score a single component by searching for similar vectors in Qdrant.

    The score is based on:
    1. How similar the nearest neighbors are (average similarity)
    2. What proportion of similar claims were legitimate vs fraudulent
    """
    try:
        results = client.query_points(
            collection_name=COLLECTION_NAME,
            query=embedding,
            query_filter={
                "must": [
                    {"key": "component", "match": {"value": component_name}}
                ]
            },
            limit=TOP_K,
            with_payload=True,
        )

        hits: list[ScoredPoint] = results.points

        if not hits:
            return ComponentScore(
                component=component_name,
                score=0.5,
                concern_level=ConcernLevel.LOW_CONCERN,
                explanation=f"No historical {component_name} data available for comparison",
            )

        # Average similarity score
        avg_similarity = sum(h.score for h in hits) / len(hits)

        # Proportion of legitimate matches
        legitimate_count = sum(
            1 for h in hits
            if h.payload and h.payload.get("label") == "legitimate"
        )
        legitimacy_ratio = legitimate_count / len(hits)

        # Combined score: blend similarity with legitimacy ratio
        # Higher similarity to legitimate claims = higher confidence
        combined = 0.4 * avg_similarity + 0.6 * legitimacy_ratio
        combined = max(0.0, min(1.0, combined))

        concern = _concern_from_score(combined)

        explanation = (
            f"Found {len(hits)} similar {component_name} records "
            f"(avg similarity: {avg_similarity:.2f}, "
            f"{legitimate_count}/{len(hits)} legitimate matches)"
        )

        return ComponentScore(
            component=component_name,
            score=round(combined, 4),
            concern_level=concern,
            explanation=explanation,
        )

    except Exception as e:
        logger.warning(f"Vector search failed for {component_name}: {e}")
        return ComponentScore(
            component=component_name,
            score=0.5,
            concern_level=ConcernLevel.LOW_CONCERN,
            explanation=f"Vector search unavailable: {str(e)[:80]}",
        )


def score(embeddings: dict[str, list[float]]) -> ScoreBreakdown:
    """Score all component embeddings against the vector database.

    Returns a ScoreBreakdown with per-component scores and an overall
    vector similarity score.
    """
    client = get_client()
    component_scores: list[ComponentScore] = []

    for component_name, embedding in embeddings.items():
        cs = _score_component(client, component_name, embedding)
        component_scores.append(cs)

    if component_scores:
        # Weighted average: verbatim gets less weight, labor/parts get more
        weights = {
            "symptom": 1.0,
            "diagnosis": 1.2,
            "parts": 1.3,
            "labor": 1.5,
            "verbatim": 0.5,
        }
        total_weight = 0.0
        weighted_sum = 0.0
        for cs in component_scores:
            w = weights.get(cs.component, 1.0)
            weighted_sum += cs.score * w
            total_weight += w

        overall = weighted_sum / total_weight if total_weight > 0 else 0.5
    else:
        overall = 0.5

    return ScoreBreakdown(
        path="vector_similarity",
        overall_score=round(overall, 4),
        component_scores=component_scores,
    )
