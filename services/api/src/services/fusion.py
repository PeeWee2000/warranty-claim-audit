"""Score fusion service — stub.

Combines vector similarity and ML model scores into a final
calibrated confidence score with explanation factors.
"""

from ..models.scoring import (
    ScoreBreakdown,
    ScoringAction,
    ScoringFactor,
    ScoringResult,
)

# Thresholds from the plan document
_AUTO_APPROVE_THRESHOLD = 0.8
_AUTO_FLAG_THRESHOLD = 0.4


def fuse(
    vector_result: ScoreBreakdown,
    ml_result: ScoreBreakdown,
    claim_id: str | None = None,
) -> ScoringResult:
    """Combine dual-path scores into a final result.

    Currently uses a simple average. A real implementation would use
    calibrated weighted ensemble with disagreement detection.
    """
    combined = (vector_result.overall_score + ml_result.overall_score) / 2

    if combined >= _AUTO_APPROVE_THRESHOLD:
        action = ScoringAction.AUTO_APPROVE
    elif combined <= _AUTO_FLAG_THRESHOLD:
        action = ScoringAction.AUTO_FLAG
    else:
        action = ScoringAction.HUMAN_REVIEW

    factors: list[ScoringFactor] = []
    for cs in vector_result.component_scores:
        factors.append(
            ScoringFactor(
                factor=cs.component,
                concern_level=cs.concern_level,
                detail=cs.explanation,
            )
        )

    components_evaluated = [
        cs.component for cs in vector_result.component_scores
    ]

    return ScoringResult(
        claim_id=claim_id,
        confidence_score=round(combined, 4),
        recommended_action=action,
        score_breakdown=[vector_result, ml_result],
        contributing_factors=factors,
        components_evaluated=components_evaluated,
    )
