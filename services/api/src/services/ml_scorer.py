"""Supervised ML scoring service using trained XGBoost model.

Extracts features from a decomposed claim and runs them through
the trained XGBoost classifier to produce a fraud probability.
"""

import json
import logging
import re
from pathlib import Path

import joblib
import numpy as np

from ..config import settings
from ..models.components import ClaimComponents
from ..models.scoring import (
    ComponentScore,
    ConcernLevel,
    ScoreBreakdown,
)

logger = logging.getLogger(__name__)

_model = None
_feature_names: list[str] | None = None

def _get_model_dir() -> Path:
    from ..config import settings
    return Path(settings.model_dir)


def _load_model():
    """Lazy-load the trained model and feature names."""
    global _model, _feature_names

    model_dir = _get_model_dir()
    model_path = model_dir / "model_calibrated.joblib"
    features_path = model_dir / "feature_names.json"

    if model_path.exists():
        _model = joblib.load(model_path)
        logger.info(f"Loaded ML model from {model_path}")
    else:
        logger.warning(f"Model not found at {model_path}, using fallback scoring")
        _model = None

    if features_path.exists():
        with open(features_path) as f:
            _feature_names = json.load(f)
    else:
        _feature_names = None


def _extract_features_from_components(components: ClaimComponents) -> dict:
    """Extract the same features used during training from live components."""
    features = {}

    # Labor features
    if components.labor:
        features["labor_hours_claimed"] = components.labor.hours_claimed
        features["book_time_hours"] = components.labor.book_time_hours or 0.0
        features["labor_vs_book_ratio"] = (
            components.labor.hours_claimed / components.labor.book_time_hours
            if components.labor.book_time_hours and components.labor.book_time_hours > 0
            else 1.0
        )
        features["labor_book_delta"] = (
            components.labor.hours_claimed - (components.labor.book_time_hours or 0.0)
        )
        rate = components.labor.labor_rate or 120.0
        features["labor_cost"] = components.labor.hours_claimed * rate
        features["cost_per_labor_hour"] = rate
    else:
        features["labor_hours_claimed"] = 0.0
        features["book_time_hours"] = 0.0
        features["labor_vs_book_ratio"] = 1.0
        features["labor_book_delta"] = 0.0
        features["labor_cost"] = 0.0
        features["cost_per_labor_hour"] = 0.0

    # Parts features
    if components.parts:
        features["parts_cost_claimed"] = components.parts.total_parts_cost or 0.0
        features["parts_count"] = len(components.parts.parts)
    else:
        features["parts_cost_claimed"] = 0.0
        features["parts_count"] = 0

    total = features["parts_cost_claimed"] + features["labor_cost"]
    features["total_claim_amount"] = total
    features["parts_to_total_ratio"] = (
        features["parts_cost_claimed"] / total if total > 0 else 0.0
    )

    # Vehicle features
    if components.vehicle:
        features["vehicle_year"] = components.vehicle.year or 2020
        features["vehicle_mileage"] = components.vehicle.mileage or 50000
        features["vehicle_age"] = 2026 - features["vehicle_year"]
        features["high_mileage"] = 1 if features["vehicle_mileage"] > 100_000 else 0
        features["low_mileage"] = 1 if features["vehicle_mileage"] < 20_000 else 0
        features["miles_per_year"] = (
            features["vehicle_mileage"] / max(features["vehicle_age"], 1)
        )
    else:
        features["vehicle_year"] = 2020
        features["vehicle_mileage"] = 50000
        features["vehicle_age"] = 6
        features["high_mileage"] = 0
        features["low_mileage"] = 0
        features["miles_per_year"] = 8333.0

    # Text features from verbatim
    text = components.verbatim.text if components.verbatim else ""
    text_lower = text.lower()
    features["text_length"] = len(text)
    features["word_count"] = len(text.split())
    features["sentence_count"] = text.count(".") + text.count("!") + text.count("?")

    # Keyword counts
    symptom_keywords = [
        "noise", "grinding", "squealing", "vibration", "leak", "warning",
        "light", "check engine", "overheating", "smell", "smoke", "stalling",
        "rough", "misfire", "shaking", "pulling", "dead", "won't start",
    ]
    features["symptom_keyword_count"] = sum(1 for kw in symptom_keywords if kw in text_lower)

    diag_keywords = [
        "found", "diagnosed", "confirmed", "tested", "measured", "worn",
        "cracked", "failed", "defective", "out of spec", "corroded",
        "leak", "fault code", "dtc",
    ]
    features["diagnosis_keyword_count"] = sum(1 for kw in diag_keywords if kw in text_lower)

    # DTC features
    dtc_pattern = re.compile(r"\b[PBCU]\d{4}\b")
    dtcs_found = dtc_pattern.findall(text)
    features["dtc_count"] = len(dtcs_found)
    features["has_dtc"] = 1 if dtcs_found else 0

    # Symptom-diagnosis overlap
    symptom_words = set()
    diag_words = set()
    if components.symptom:
        symptom_words = set(components.symptom.description.lower().split())
    if components.diagnosis:
        diag_words = set(components.diagnosis.description.lower().split())

    if symptom_words and diag_words:
        overlap = len(symptom_words & diag_words)
        features["symptom_diag_overlap"] = overlap / max(len(symptom_words | diag_words), 1)
    else:
        features["symptom_diag_overlap"] = 0.0

    # Maintenance items
    maintenance_items = ["cabin air filter", "wiper blade", "engine air filter",
                         "fuel system cleaner", "transmission fluid"]
    features["maintenance_items_count"] = sum(1 for item in maintenance_items if item in text_lower)

    return features


def _concern_from_fraud_prob(prob: float) -> ConcernLevel:
    """Map fraud probability to concern level."""
    if prob < 0.2:
        return ConcernLevel.NORMAL
    elif prob < 0.4:
        return ConcernLevel.LOW_CONCERN
    elif prob < 0.65:
        return ConcernLevel.MODERATE_CONCERN
    else:
        return ConcernLevel.HIGH_CONCERN


def score(components: ClaimComponents) -> ScoreBreakdown:
    """Score a claim using the trained ML model.

    Returns a legitimacy score (1.0 = legitimate, 0.0 = fraudulent).
    """
    global _model, _feature_names

    if _model is None:
        _load_model()

    features = _extract_features_from_components(components)

    if _model is not None and _feature_names is not None:
        # Build feature vector in training order
        feature_vector = []
        for fname in _feature_names:
            feature_vector.append(features.get(fname, 0.0))

        X = np.array([feature_vector])
        fraud_prob = _model.predict_proba(X)[0][1]
        legitimacy_score = 1.0 - fraud_prob
    else:
        # Fallback heuristic scoring when model unavailable
        legitimacy_score = _heuristic_score(features)
        fraud_prob = 1.0 - legitimacy_score

    concern = _concern_from_fraud_prob(fraud_prob)

    # Build component-level insights
    component_scores = []

    # Labor assessment
    labor_ratio = features.get("labor_vs_book_ratio", 1.0)
    if labor_ratio > 2.0:
        labor_concern = ConcernLevel.HIGH_CONCERN
        labor_score = max(0.1, 1.0 - (labor_ratio - 1.0) * 0.3)
    elif labor_ratio > 1.5:
        labor_concern = ConcernLevel.MODERATE_CONCERN
        labor_score = max(0.3, 1.0 - (labor_ratio - 1.0) * 0.3)
    elif labor_ratio > 1.2:
        labor_concern = ConcernLevel.LOW_CONCERN
        labor_score = 0.7
    else:
        labor_concern = ConcernLevel.NORMAL
        labor_score = 0.9

    component_scores.append(ComponentScore(
        component="labor",
        score=round(labor_score, 4),
        concern_level=labor_concern,
        explanation=f"Labor/book ratio: {labor_ratio:.2f}x",
    ))

    # Maintenance items check
    maint_count = features.get("maintenance_items_count", 0)
    if maint_count > 0:
        component_scores.append(ComponentScore(
            component="parts",
            score=round(max(0.3, 1.0 - maint_count * 0.25), 4),
            concern_level=ConcernLevel.MODERATE_CONCERN if maint_count > 1 else ConcernLevel.LOW_CONCERN,
            explanation=f"{maint_count} maintenance/unrelated items found in parts list",
        ))

    return ScoreBreakdown(
        path="ml_model",
        overall_score=round(legitimacy_score, 4),
        component_scores=component_scores,
    )


def _heuristic_score(features: dict) -> float:
    """Simple heuristic fallback when ML model is not available."""
    score = 0.75  # Start with neutral-positive

    labor_ratio = features.get("labor_vs_book_ratio", 1.0)
    if labor_ratio > 2.0:
        score -= 0.3
    elif labor_ratio > 1.5:
        score -= 0.15

    maint = features.get("maintenance_items_count", 0)
    score -= maint * 0.1

    return max(0.05, min(0.95, score))
