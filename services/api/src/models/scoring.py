"""Scoring output schemas.

These models define the structure of confidence scores returned by the
dual scoring engine (vector similarity + supervised ML) and the fused output.
"""

from enum import Enum

from pydantic import BaseModel, Field


class ScoringAction(str, Enum):
    """Recommended action based on the final confidence score."""

    AUTO_APPROVE = "auto_approve"
    HUMAN_REVIEW = "human_review"
    AUTO_FLAG = "auto_flag"


class ConcernLevel(str, Enum):
    """Concern level for an individual scoring factor."""

    NORMAL = "normal"
    LOW_CONCERN = "low_concern"
    MODERATE_CONCERN = "moderate_concern"
    HIGH_CONCERN = "high_concern"


class ComponentScore(BaseModel):
    """Score for a single claim component from a single scoring path."""

    component: str = Field(..., description="Component name (symptom, diagnosis, parts, labor)")
    score: float = Field(..., ge=0.0, le=1.0, description="Confidence score (1.0 = fully legitimate)")
    concern_level: ConcernLevel = ConcernLevel.NORMAL
    explanation: str = Field(default="", description="Human-readable explanation for this score")


class ScoreBreakdown(BaseModel):
    """Detailed breakdown from one scoring path."""

    path: str = Field(..., description="Scoring path identifier (vector_similarity or ml_model)")
    overall_score: float = Field(..., ge=0.0, le=1.0)
    component_scores: list[ComponentScore] = Field(default_factory=list)


class ScoringFactor(BaseModel):
    """A single contributing factor to the final score."""

    factor: str = Field(..., description="Factor name")
    concern_level: ConcernLevel
    detail: str = Field(default="", description="Explanation of this factor's contribution")


class ScoringResult(BaseModel):
    """The complete scoring output for a single claim.

    This is the primary response returned by the /score endpoint.
    """

    claim_id: str | None = Field(default=None, description="Echo of the input claim ID")
    confidence_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Final fused confidence score (1.0 = fully legitimate, 0.0 = highly suspicious)",
    )
    recommended_action: ScoringAction
    score_breakdown: list[ScoreBreakdown] = Field(
        default_factory=list,
        description="Per-path scoring details (vector similarity, ML model)",
    )
    contributing_factors: list[ScoringFactor] = Field(
        default_factory=list,
        description="Key factors that influenced the final score",
    )
    components_evaluated: list[str] = Field(
        default_factory=list,
        description="Which claim components were successfully scored",
    )
