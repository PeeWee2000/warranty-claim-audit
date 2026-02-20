"""Validation rules for synthetic claims.

Ensures generated claims are internally consistent and realistic
before they enter the training pipeline.
"""

from dataclasses import dataclass


@dataclass
class ValidationResult:
    valid: bool
    errors: list[str]


def validate_claim(claim: dict) -> ValidationResult:
    """Run rule-based validation on a synthetic claim."""
    errors: list[str] = []

    # Text must be present and non-trivial
    if not claim.get("text") or len(claim["text"]) < 20:
        errors.append("Claim text is missing or too short")

    # Vehicle year must be reasonable
    year = claim.get("vehicle_year")
    if year and (year < 1990 or year > 2030):
        errors.append(f"Vehicle year {year} is out of range")

    # Mileage must be non-negative
    mileage = claim.get("vehicle_mileage")
    if mileage is not None and mileage < 0:
        errors.append(f"Negative mileage: {mileage}")

    # Labor hours should be positive and within reason
    hours = claim.get("labor_hours_claimed")
    if hours is not None:
        if hours <= 0:
            errors.append(f"Non-positive labor hours: {hours}")
        if hours > 40:
            errors.append(f"Unrealistic labor hours: {hours}")

    # Parts cost should be non-negative
    parts_cost = claim.get("parts_cost_claimed")
    if parts_cost is not None and parts_cost < 0:
        errors.append(f"Negative parts cost: {parts_cost}")

    # Total should roughly equal labor + parts
    total = claim.get("total_claim_amount")
    if total is not None and parts_cost is not None and hours is not None:
        # Allow 20% tolerance for rounding
        expected_min = parts_cost + (hours * 80)  # low rate
        expected_max = parts_cost + (hours * 200)  # high rate
        if total < expected_min * 0.5 or total > expected_max * 2:
            errors.append(
                f"Total ${total} seems inconsistent with parts ${parts_cost} + {hours}hrs"
            )

    # Label must be present
    if claim.get("label") not in ("legitimate", "fraudulent"):
        errors.append(f"Invalid label: {claim.get('label')}")

    return ValidationResult(valid=len(errors) == 0, errors=errors)
