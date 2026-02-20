"""Synthetic warranty claim generator.

Produces realistic synthetic claims with known labels for training.
Generates both legitimate claims and claims exhibiting known fraud patterns.
"""

import random
from datetime import date, timedelta

from .templates.claim_templates import (
    FRAUD_PATTERNS,
    LABOR_RATES,
    REPAIR_SCENARIOS,
    VEHICLES,
    FraudPattern,
    RepairScenario,
)


def _random_vehicle() -> dict:
    """Pick a random vehicle with a random year and mileage."""
    template = random.choice(VEHICLES)
    year = random.choice(list(template["years"]))
    age = date.today().year - year
    # Roughly 12k miles/year with some variance
    base_mileage = age * 12_000
    mileage = max(1000, base_mileage + random.randint(-5000, 5000))
    return {
        "make": template["make"],
        "model": template["model"],
        "year": year,
        "mileage": mileage,
    }


def _random_date(days_back: int = 365) -> date:
    """Generate a random claim date within the given window."""
    offset = random.randint(0, days_back)
    return date.today() - timedelta(days=offset)


def _build_narrative(
    vehicle: dict,
    scenario: RepairScenario,
    hours: float,
    region: str,
) -> str:
    """Assemble a realistic claim narrative from components."""
    symptom = random.choice(scenario.symptoms)
    diagnosis = random.choice(scenario.diagnoses)

    parts_text = ", ".join(p["name"] for p in scenario.parts)
    parts_cost = sum(p["cost"] for p in scenario.parts)

    rate = LABOR_RATES.get(region, LABOR_RATES["default"])
    labor_cost = hours * rate

    lines = [
        f"{vehicle['year']} {vehicle['make']} {vehicle['model']}, "
        f"{vehicle['mileage']:,} miles.",
        f"Customer states: {symptom}.",
        f"Technician diagnosis: {diagnosis}.",
        f"Replaced: {parts_text}.",
        f"Parts total: ${parts_cost:.2f}.",
        f"Labor: {hours:.1f} hours at ${rate:.2f}/hr (${labor_cost:.2f}).",
        f"Book time: {scenario.book_time_hours:.1f} hours.",
    ]
    return " ".join(lines)


def generate_legitimate_claim() -> dict:
    """Generate a single legitimate synthetic warranty claim."""
    vehicle = _random_vehicle()
    scenario = random.choice(REPAIR_SCENARIOS)
    region = random.choice(list(LABOR_RATES.keys()))

    # Legitimate claims stay within reasonable labor range
    hours = round(
        random.uniform(scenario.labor_range[0], scenario.labor_range[1]), 1
    )

    rate = LABOR_RATES.get(region, LABOR_RATES["default"])
    parts_cost = sum(p["cost"] for p in scenario.parts)
    total = parts_cost + (hours * rate)

    narrative = _build_narrative(vehicle, scenario, hours, region)

    return {
        "text": narrative,
        "label": "legitimate",
        "fraud_type": None,
        "vehicle_make": vehicle["make"],
        "vehicle_model": vehicle["model"],
        "vehicle_year": vehicle["year"],
        "vehicle_mileage": vehicle["mileage"],
        "labor_hours_claimed": hours,
        "parts_cost_claimed": parts_cost,
        "total_claim_amount": round(total, 2),
        "scenario": scenario.name,
        "region": region,
        "claim_date": _random_date().isoformat(),
    }


def _apply_fraud_pattern(
    claim: dict,
    scenario: RepairScenario,
    pattern: FraudPattern,
) -> dict:
    """Mutate a legitimate claim to exhibit a fraud pattern."""
    claim = claim.copy()
    claim["label"] = "fraudulent"
    claim["fraud_type"] = pattern.name

    if pattern.name == "labor_inflation":
        # Inflate labor hours to 2-4x book time
        inflated = round(scenario.book_time_hours * random.uniform(2.0, 4.0), 1)
        rate = LABOR_RATES.get(claim["region"], LABOR_RATES["default"])
        claim["labor_hours_claimed"] = inflated
        claim["total_claim_amount"] = round(
            claim["parts_cost_claimed"] + (inflated * rate), 2
        )
        # Rebuild narrative with inflated hours
        vehicle = {
            "make": claim["vehicle_make"],
            "model": claim["vehicle_model"],
            "year": claim["vehicle_year"],
            "mileage": claim["vehicle_mileage"],
        }
        claim["text"] = _build_narrative(vehicle, scenario, inflated, claim["region"])

    elif pattern.name == "unnecessary_parts":
        # Add unrelated parts to the claim
        extra_parts = random.sample(
            [
                ("Cabin Air Filter", 25.00),
                ("Wiper Blades (pair)", 40.00),
                ("Engine Air Filter", 30.00),
                ("Transmission Fluid Flush", 150.00),
                ("Fuel System Cleaner", 85.00),
            ],
            k=random.randint(1, 3),
        )
        extra_cost = sum(cost for _, cost in extra_parts)
        extras_text = ", ".join(name for name, _ in extra_parts)
        claim["parts_cost_claimed"] += extra_cost
        claim["total_claim_amount"] += extra_cost
        claim["text"] += f" Also replaced: {extras_text} (${extra_cost:.2f})."

    elif pattern.name == "symptom_repair_mismatch":
        # Pick a different scenario's repair for the original symptom
        other_scenarios = [s for s in REPAIR_SCENARIOS if s.name != scenario.name]
        wrong_scenario = random.choice(other_scenarios)
        wrong_diag = random.choice(wrong_scenario.diagnoses)
        wrong_parts = ", ".join(p["name"] for p in wrong_scenario.parts)

        # Keep original symptom but swap diagnosis and parts
        original_symptom = random.choice(scenario.symptoms)
        vehicle = {
            "make": claim["vehicle_make"],
            "model": claim["vehicle_model"],
            "year": claim["vehicle_year"],
            "mileage": claim["vehicle_mileage"],
        }
        rate = LABOR_RATES.get(claim["region"], LABOR_RATES["default"])
        hours = claim["labor_hours_claimed"]

        wrong_parts_cost = sum(p["cost"] for p in wrong_scenario.parts)
        claim["parts_cost_claimed"] = wrong_parts_cost
        claim["total_claim_amount"] = round(wrong_parts_cost + (hours * rate), 2)
        claim["text"] = (
            f"{vehicle['year']} {vehicle['make']} {vehicle['model']}, "
            f"{vehicle['mileage']:,} miles. "
            f"Customer states: {original_symptom}. "
            f"Technician diagnosis: {wrong_diag}. "
            f"Replaced: {wrong_parts}. "
            f"Parts total: ${wrong_parts_cost:.2f}. "
            f"Labor: {hours:.1f} hours at ${rate:.2f}/hr."
        )

    return claim


def generate_fraudulent_claim(pattern_name: str | None = None) -> dict:
    """Generate a synthetic claim exhibiting a specific fraud pattern.

    Args:
        pattern_name: Name of the fraud pattern to apply. If None, picks randomly.
    """
    if pattern_name:
        matching = [p for p in FRAUD_PATTERNS if p.name == pattern_name]
        if not matching:
            raise ValueError(
                f"Unknown fraud pattern: {pattern_name}. "
                f"Available: {[p.name for p in FRAUD_PATTERNS]}"
            )
        pattern = matching[0]
    else:
        # Only use patterns we have implemented manipulations for
        implemented = ["labor_inflation", "unnecessary_parts", "symptom_repair_mismatch"]
        pattern = random.choice([p for p in FRAUD_PATTERNS if p.name in implemented])

    # Start from a legitimate claim, then corrupt it
    claim = generate_legitimate_claim()
    scenario = next(s for s in REPAIR_SCENARIOS if s.name == claim["scenario"])
    return _apply_fraud_pattern(claim, scenario, pattern)


def generate_dataset(
    n_legitimate: int = 700,
    n_fraudulent: int = 300,
    seed: int | None = None,
) -> list[dict]:
    """Generate a balanced synthetic dataset.

    Args:
        n_legitimate: Number of legitimate claims to generate.
        n_fraudulent: Number of fraudulent claims to generate.
        seed: Random seed for reproducibility.

    Returns:
        List of claim dicts with 'label' and 'fraud_type' fields.
    """
    if seed is not None:
        random.seed(seed)

    claims: list[dict] = []

    for _ in range(n_legitimate):
        claims.append(generate_legitimate_claim())

    # Distribute fraud patterns roughly evenly
    implemented_patterns = ["labor_inflation", "unnecessary_parts", "symptom_repair_mismatch"]
    for i in range(n_fraudulent):
        pattern = implemented_patterns[i % len(implemented_patterns)]
        claims.append(generate_fraudulent_claim(pattern))

    random.shuffle(claims)
    return claims
