"""Supervised ML scoring service — stub.

Will run feature extraction and XGBoost inference
to produce a pattern-based fraud confidence score.
"""

from ..models.components import ClaimComponents
from ..models.scoring import ScoreBreakdown


def score(components: ClaimComponents) -> ScoreBreakdown:
    """Placeholder: returns neutral scores.

    A real implementation would extract structured + cross-component
    features and run them through a trained XGBoost classifier.
    """
    return ScoreBreakdown(
        path="ml_model",
        overall_score=0.5,
        component_scores=[],
    )
