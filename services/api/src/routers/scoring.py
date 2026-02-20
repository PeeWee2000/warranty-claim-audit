"""Scoring API routes."""

from fastapi import APIRouter

from ..models.claim import RawClaim
from ..models.scoring import ScoringResult
from ..services import decomposer, embedder, fusion, ml_scorer, vector_scorer

router = APIRouter(prefix="/api", tags=["scoring"])


@router.post("/score", response_model=ScoringResult)
async def score_claim(claim: RawClaim) -> ScoringResult:
    """Score a warranty claim and return detailed confidence breakdown.

    Accepts a raw claim (text + optional structured fields), decomposes it
    into semantic components, runs dual scoring paths, and returns a fused
    confidence score with contributing factors.
    """
    # 1. Decompose claim into components
    components = decomposer.decompose(claim)

    # 2. Generate embeddings (stub)
    embeddings = embedder.embed_components(components)

    # 3. Run dual scoring paths (stubs)
    vec_scores = vector_scorer.score(embeddings)
    ml_scores = ml_scorer.score(components)

    # 4. Fuse scores
    result = fusion.fuse(vec_scores, ml_scores, claim_id=claim.metadata.claim_id)

    return result
