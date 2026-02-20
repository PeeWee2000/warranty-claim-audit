"""Vector similarity scoring service — stub.

Will query Qdrant with per-component embeddings and compute
similarity-based confidence scores.
"""

from ..models.scoring import ComponentScore, ScoreBreakdown


def score(embeddings: dict[str, list[float]]) -> ScoreBreakdown:
    """Placeholder: returns neutral scores.

    A real implementation would search Qdrant for nearest neighbors
    per component and derive consistency/anomaly scores.
    """
    component_scores = [
        ComponentScore(component=name, score=0.5, explanation="Not yet implemented")
        for name in embeddings
    ]
    return ScoreBreakdown(
        path="vector_similarity",
        overall_score=0.5,
        component_scores=component_scores,
    )
