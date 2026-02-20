"""Feature engineering pipeline for XGBoost training.

Extracts structured, cross-component, and statistical features from
decomposed warranty claims for the supervised ML scoring path.
"""

import numpy as np
import pandas as pd


def extract_features(claims: list[dict]) -> pd.DataFrame:
    """Convert raw synthetic claims into a feature matrix for XGBoost.

    Args:
        claims: List of claim dicts from the synthetic generator.

    Returns:
        DataFrame with one row per claim and engineered features as columns.
    """
    rows = []
    for claim in claims:
        row = _extract_single(claim)
        rows.append(row)
    return pd.DataFrame(rows)


def _extract_single(claim: dict) -> dict:
    """Extract features from a single claim."""
    text = claim.get("text", "")
    text_lower = text.lower()

    features = {}

    # --- Numeric features ---
    features["labor_hours_claimed"] = claim.get("labor_hours_claimed", 0.0)
    features["parts_cost_claimed"] = claim.get("parts_cost_claimed", 0.0)
    features["total_claim_amount"] = claim.get("total_claim_amount", 0.0)
    features["vehicle_mileage"] = claim.get("vehicle_mileage", 0)
    features["vehicle_year"] = claim.get("vehicle_year", 2020)
    features["vehicle_age"] = 2026 - features["vehicle_year"]

    # --- Labor features ---
    book_time = _extract_book_time(text)
    features["book_time_hours"] = book_time
    features["labor_vs_book_ratio"] = (
        features["labor_hours_claimed"] / book_time if book_time > 0 else 1.0
    )
    features["labor_book_delta"] = features["labor_hours_claimed"] - book_time

    # --- Cost features ---
    labor_cost = features["total_claim_amount"] - features["parts_cost_claimed"]
    features["labor_cost"] = max(labor_cost, 0)
    features["parts_to_total_ratio"] = (
        features["parts_cost_claimed"] / features["total_claim_amount"]
        if features["total_claim_amount"] > 0
        else 0.0
    )
    features["cost_per_labor_hour"] = (
        labor_cost / features["labor_hours_claimed"]
        if features["labor_hours_claimed"] > 0
        else 0.0
    )

    # --- Text complexity features ---
    features["text_length"] = len(text)
    features["word_count"] = len(text.split())
    features["sentence_count"] = text.count(".") + text.count("!") + text.count("?")

    # --- Symptom keyword features ---
    symptom_keywords = [
        "noise", "grinding", "squealing", "vibration", "leak", "warning",
        "light", "check engine", "overheating", "smell", "smoke", "stalling",
        "rough", "misfire", "shaking", "pulling", "dead", "won't start",
    ]
    features["symptom_keyword_count"] = sum(
        1 for kw in symptom_keywords if kw in text_lower
    )

    # --- Diagnosis keyword features ---
    diag_keywords = [
        "found", "diagnosed", "confirmed", "tested", "measured", "worn",
        "cracked", "failed", "defective", "out of spec", "corroded",
        "leak", "fault code", "dtc",
    ]
    features["diagnosis_keyword_count"] = sum(
        1 for kw in diag_keywords if kw in text_lower
    )

    # --- DTC features ---
    import re
    dtc_pattern = re.compile(r"\b[PBCU]\d{4}\b")
    dtcs_found = dtc_pattern.findall(text)
    features["dtc_count"] = len(dtcs_found)
    features["has_dtc"] = 1 if dtcs_found else 0

    # --- Cross-component features ---
    # Symptom-diagnosis text overlap (simple word overlap ratio)
    symptom_words = set()
    diag_words = set()
    sentences = text.split(".")
    for s in sentences:
        s_lower = s.lower().strip()
        if any(kw in s_lower for kw in ["customer states", "complaint", "reports"]):
            symptom_words.update(s_lower.split())
        elif any(kw in s_lower for kw in ["diagnosis", "found", "confirmed", "tested"]):
            diag_words.update(s_lower.split())

    if symptom_words and diag_words:
        overlap = len(symptom_words & diag_words)
        features["symptom_diag_overlap"] = overlap / max(
            len(symptom_words | diag_words), 1
        )
    else:
        features["symptom_diag_overlap"] = 0.0

    # --- Parts count features ---
    common_parts = [
        "brake pad", "rotor", "caliper", "strut", "shock", "alternator",
        "starter", "battery", "water pump", "thermostat", "radiator",
        "spark plug", "ignition coil", "fuel pump", "oxygen sensor",
        "catalytic converter", "wheel bearing", "cv axle", "control arm",
        "tie rod", "ball joint", "ac compressor", "serpentine belt",
        "timing belt", "timing chain", "power steering", "fuel injector",
        "muffler", "clutch", "flywheel", "transmission",
        "cabin air filter", "wiper blade", "engine air filter",
    ]
    parts_found = [p for p in common_parts if p in text_lower]
    features["parts_count"] = len(parts_found)

    # Flag potentially unnecessary/unrelated parts
    # (maintenance items in a repair claim context)
    maintenance_items = ["cabin air filter", "wiper blade", "engine air filter",
                         "fuel system cleaner", "transmission fluid"]
    features["maintenance_items_count"] = sum(
        1 for item in maintenance_items if item in text_lower
    )

    # --- Mileage-based features ---
    features["high_mileage"] = 1 if features["vehicle_mileage"] > 100_000 else 0
    features["low_mileage"] = 1 if features["vehicle_mileage"] < 20_000 else 0
    features["miles_per_year"] = (
        features["vehicle_mileage"] / max(features["vehicle_age"], 1)
    )

    return features


def _extract_book_time(text: str) -> float:
    """Extract book time hours from claim text."""
    import re
    match = re.search(r"book\s*time[:\s]*(\d+\.?\d*)", text, re.IGNORECASE)
    if match:
        return float(match.group(1))
    return 0.0


def get_feature_names() -> list[str]:
    """Return the ordered list of feature column names."""
    # Generate a dummy claim to get column names
    dummy = {
        "text": "Test claim text for feature extraction.",
        "labor_hours_claimed": 1.0,
        "parts_cost_claimed": 100.0,
        "total_claim_amount": 200.0,
        "vehicle_mileage": 50000,
        "vehicle_year": 2020,
    }
    df = extract_features([dummy])
    return list(df.columns)
