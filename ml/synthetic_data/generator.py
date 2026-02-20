"""Enhanced synthetic warranty claim generator.

Uses comprehensive domain databases (DTCs, vehicles, parts, labor) to produce
realistic, diverse synthetic claims with known labels for training.
"""

import random
import re
from datetime import date, timedelta

from .templates.dtc_database import DTC_DATABASE
from .templates.vehicle_database import VEHICLES
from .templates.parts_database import PARTS
from .templates.labor_database import LABOR_OPERATIONS, LABOR_RATES_BY_REGION


# ── Helpers ──────────────────────────────────────────────────────────────

def _pick_vehicle() -> dict:
    """Select a random vehicle with plausible year and mileage."""
    v = random.choice(VEHICLES)
    year = random.choice(list(v["years"]))
    age = max(1, date.today().year - year)
    base_miles = age * random.randint(9_000, 16_000)
    mileage = max(500, base_miles + random.randint(-3000, 3000))
    return {
        "make": v["make"],
        "model": v["model"],
        "year": year,
        "mileage": mileage,
        "vehicle_class": v["vehicle_class"],
        "warranty_bb_miles": v["warranty_bb_miles"],
        "warranty_bb_months": v["warranty_bb_months"],
        "warranty_pt_miles": v.get("warranty_pt_miles", 60_000),
        "engine_types": v.get("engine_types", ["I4"]),
    }


def _pick_labor_rate() -> tuple[float, str]:
    """Pick a realistic labor rate from a random region."""
    region_data = random.choice(LABOR_RATES_BY_REGION)
    region = region_data["region"]
    # 80% chance dealer, 20% independent
    if random.random() < 0.8:
        lo, hi = region_data["dealer_rate_range"]
    else:
        lo, hi = region_data["independent_rate_range"]
    rate = round(random.uniform(lo, hi), 2)
    return rate, region


def _pick_dtc() -> dict | None:
    """Pick a random DTC, or None (30% of claims have no DTC)."""
    if random.random() < 0.3:
        return None
    return random.choice(DTC_DATABASE)


def _pick_related_parts(dtc: dict | None, scenario_parts: list[str], count: int = None) -> list[dict]:
    """Select parts that are plausibly related to the repair."""
    selected = []

    # If we have a DTC, prefer its common parts
    part_names_to_find = list(scenario_parts)
    if dtc:
        part_names_to_find.extend(dtc.get("common_parts", []))

    # Deduplicate
    part_names_to_find = list(dict.fromkeys(part_names_to_find))

    if count is None:
        count = random.randint(1, min(4, len(part_names_to_find)))

    for name in part_names_to_find[:count]:
        # Try to find in parts database
        matches = [p for p in PARTS if name.lower() in p["name"].lower()]
        if matches:
            p = random.choice(matches)
            cost = round(random.uniform(p["price_range"][0], p["price_range"][1]), 2)
            selected.append({"name": p["name"], "cost": cost, "is_wear_item": p["is_wear_item"]})
        else:
            # Fallback: use the name with estimated cost
            selected.append({"name": name, "cost": round(random.uniform(30, 300), 2), "is_wear_item": False})

    return selected


def _customer_verbatim(symptoms: list[str]) -> str:
    """Generate realistic customer language from symptom list."""
    intros = [
        "Customer states", "Customer reports", "Customer complains",
        "Customer says", "Owner reports", "Driver states",
    ]
    connectors = [
        ". Also noticed", ". Additionally", ". Vehicle also",
        " and", ". Customer also mentions",
    ]
    intro = random.choice(intros)
    symptom = random.choice(symptoms)

    # Sometimes add a qualifier
    qualifiers = [
        "", " for the past few weeks", " since last month",
        " intermittently", " especially in cold weather",
        " when driving at highway speeds", " during acceleration",
        " when braking", " at idle", " after the vehicle warms up",
    ]
    qualifier = random.choice(qualifiers)

    text = f"{intro}: {symptom}{qualifier}"

    # 40% chance of a second symptom
    if len(symptoms) > 1 and random.random() < 0.4:
        other = random.choice([s for s in symptoms if s != symptom])
        connector = random.choice(connectors)
        text += f"{connector} {other.lower()}"

    return text


def _technician_diagnosis(dtc: dict | None, repairs: list[str]) -> str:
    """Generate realistic technician diagnosis narrative."""
    prefixes = [
        "Technician diagnosis:", "Upon inspection,", "Diagnostic findings:",
        "Tech found:", "Inspection revealed:", "After thorough inspection,",
    ]

    dtc_text = ""
    if dtc:
        dtc_text = f" Retrieved DTC {dtc['code']} - {dtc['description']}."

    repair_desc = random.choice(repairs) if repairs else "Component failure confirmed"

    verification_phrases = [
        "Confirmed via visual inspection",
        "Verified with diagnostic scan tool",
        "Tested and confirmed",
        "Measured and found out of specification",
        "Failure confirmed during road test",
        "Component tested and failed bench test",
    ]

    prefix = random.choice(prefixes)
    verify = random.choice(verification_phrases)

    return f"{prefix}{dtc_text} {repair_desc}. {verify}."


def _build_narrative(
    vehicle: dict,
    symptom_text: str,
    diagnosis_text: str,
    parts: list[dict],
    labor_hours: float,
    book_time: float,
    rate: float,
) -> str:
    """Assemble a complete claim narrative."""
    parts_text = ", ".join(p["name"] for p in parts)
    parts_cost = sum(p["cost"] for p in parts)
    labor_cost = labor_hours * rate

    lines = [
        f"{vehicle['year']} {vehicle['make']} {vehicle['model']}, "
        f"{vehicle['mileage']:,} miles.",
        f"{symptom_text}.",
        f"{diagnosis_text}",
        f"Replaced: {parts_text}.",
        f"Parts total: ${parts_cost:.2f}.",
        f"Labor: {labor_hours:.1f} hours at ${rate:.2f}/hr (${labor_cost:.2f}).",
        f"Book time: {book_time:.1f} hours.",
    ]
    return " ".join(lines)


# ── Core generators ──────────────────────────────────────────────────────

def generate_legitimate_claim() -> dict:
    """Generate a single legitimate synthetic warranty claim."""
    vehicle = _pick_vehicle()
    rate, region = _pick_labor_rate()
    dtc = _pick_dtc()

    # Pick a DTC-driven scenario or a random labor operation
    if dtc:
        symptoms = dtc["common_symptoms"]
        repairs = dtc["common_repairs"]
        part_names = dtc["common_parts"]
        book_time = dtc["typical_labor_hours"]
        scenario_name = f"dtc_{dtc['code']}"
    else:
        # Pick a random labor operation
        op = random.choice(LABOR_OPERATIONS)
        book_time = op["book_time_hours"]
        scenario_name = op["operation_name"]
        # Generate generic symptoms based on category
        symptoms = _generic_symptoms(op["category"])
        repairs = [f"Perform {op['operation_name']}"]
        part_names = _parts_for_category(op["category"])

    # Legitimate claims have labor within reasonable range of book time
    labor_variance = random.uniform(0.85, 1.25)
    labor_hours = round(book_time * labor_variance, 1)
    labor_hours = max(0.3, labor_hours)

    parts = _pick_related_parts(dtc, part_names)
    parts_cost = round(sum(p["cost"] for p in parts), 2)
    total = round(parts_cost + (labor_hours * rate), 2)

    symptom_text = _customer_verbatim(symptoms)
    diagnosis_text = _technician_diagnosis(dtc, repairs)
    narrative = _build_narrative(vehicle, symptom_text, diagnosis_text, parts, labor_hours, book_time, rate)

    return {
        "text": narrative,
        "label": "legitimate",
        "fraud_type": None,
        "vehicle_make": vehicle["make"],
        "vehicle_model": vehicle["model"],
        "vehicle_year": vehicle["year"],
        "vehicle_mileage": vehicle["mileage"],
        "vehicle_class": vehicle["vehicle_class"],
        "labor_hours_claimed": labor_hours,
        "book_time_hours": book_time,
        "parts_cost_claimed": parts_cost,
        "total_claim_amount": total,
        "labor_rate": rate,
        "scenario": scenario_name,
        "region": region,
        "claim_date": _random_date().isoformat(),
        "dtc_code": dtc["code"] if dtc else None,
        "parts_list": [p["name"] for p in parts],
    }


def generate_fraudulent_claim(pattern: str | None = None) -> dict:
    """Generate a claim exhibiting a specific fraud pattern."""
    patterns = ["labor_inflation", "unnecessary_parts", "symptom_repair_mismatch",
                "phantom_repair", "upcoding"]
    if pattern is None:
        pattern = random.choice(patterns)

    # Start from a legitimate base
    claim = generate_legitimate_claim()
    claim["label"] = "fraudulent"
    claim["fraud_type"] = pattern

    if pattern == "labor_inflation":
        _apply_labor_inflation(claim)
    elif pattern == "unnecessary_parts":
        _apply_unnecessary_parts(claim)
    elif pattern == "symptom_repair_mismatch":
        _apply_symptom_mismatch(claim)
    elif pattern == "phantom_repair":
        _apply_phantom_repair(claim)
    elif pattern == "upcoding":
        _apply_upcoding(claim)

    return claim


def _apply_labor_inflation(claim: dict) -> None:
    """Inflate labor hours to 2-5x book time."""
    book = claim.get("book_time_hours", 1.0)
    multiplier = random.uniform(2.0, 5.0)
    inflated = round(book * multiplier, 1)
    claim["labor_hours_claimed"] = inflated
    rate = claim.get("labor_rate", 120.0)
    claim["total_claim_amount"] = round(
        claim["parts_cost_claimed"] + (inflated * rate), 2
    )
    # Update narrative
    claim["text"] = re.sub(
        r"Labor: [\d.]+ hours",
        f"Labor: {inflated} hours",
        claim["text"],
    )


def _apply_unnecessary_parts(claim: dict) -> None:
    """Add unrelated maintenance items to the claim."""
    # Pick 1-3 unrelated parts (maintenance/wear items from different categories)
    unrelated_categories = ["Body", "HVAC", "Fuel System"]
    extras = []
    for _ in range(random.randint(1, 3)):
        candidates = [p for p in PARTS if p["category"] in unrelated_categories and p["is_wear_item"]]
        if not candidates:
            candidates = [p for p in PARTS if p["is_wear_item"]]
        if candidates:
            p = random.choice(candidates)
            cost = round(random.uniform(p["price_range"][0], p["price_range"][1]), 2)
            extras.append({"name": p["name"], "cost": cost})

    if extras:
        extra_cost = sum(e["cost"] for e in extras)
        extra_names = ", ".join(e["name"] for e in extras)
        claim["parts_cost_claimed"] += round(extra_cost, 2)
        claim["total_claim_amount"] += round(extra_cost, 2)
        claim["parts_list"].extend(e["name"] for e in extras)
        claim["text"] += f" Also replaced: {extra_names} (${extra_cost:.2f})."


def _apply_symptom_mismatch(claim: dict) -> None:
    """Swap the diagnosis/repair to something unrelated to the symptom."""
    # Pick a completely different DTC for the repair
    original_dtc = claim.get("dtc_code")
    other_dtcs = [d for d in DTC_DATABASE if d["code"] != original_dtc and d["category"] == "powertrain"]
    if not other_dtcs:
        other_dtcs = DTC_DATABASE

    wrong_dtc = random.choice(other_dtcs)
    wrong_repair = random.choice(wrong_dtc["common_repairs"])
    wrong_parts = _pick_related_parts(wrong_dtc, wrong_dtc["common_parts"], count=2)

    # Keep original symptom, but replace diagnosis and parts
    parts_cost = round(sum(p["cost"] for p in wrong_parts), 2)
    claim["parts_cost_claimed"] = parts_cost
    claim["parts_list"] = [p["name"] for p in wrong_parts]
    claim["total_claim_amount"] = round(
        parts_cost + (claim["labor_hours_claimed"] * claim.get("labor_rate", 120.0)), 2
    )

    # Replace diagnosis in narrative
    claim["text"] = re.sub(
        r"(Technician diagnosis:|Upon inspection,|Tech found:|Diagnostic findings:|Inspection revealed:|After thorough inspection,).*?\.",
        f"Technician diagnosis: {wrong_repair}. Retrieved DTC {wrong_dtc['code']}.",
        claim["text"],
        count=1,
    )


def _apply_phantom_repair(claim: dict) -> None:
    """Create suspicious timing — vehicle too new or recently serviced."""
    # Make vehicle very low mileage (warranty padding)
    claim["vehicle_mileage"] = random.randint(500, 5000)
    claim["text"] = re.sub(
        r"[\d,]+ miles",
        f"{claim['vehicle_mileage']:,} miles",
        claim["text"],
    )
    # Also inflate slightly
    claim["labor_hours_claimed"] = round(claim["labor_hours_claimed"] * 1.5, 1)
    rate = claim.get("labor_rate", 120.0)
    claim["total_claim_amount"] = round(
        claim["parts_cost_claimed"] + (claim["labor_hours_claimed"] * rate), 2
    )


def _apply_upcoding(claim: dict) -> None:
    """Bill for expensive parts but plausibly install cheaper ones."""
    # Find the most expensive part in the claim and replace with a premium version
    expensive_parts = sorted(PARTS, key=lambda p: p["price_range"][1], reverse=True)[:20]
    if expensive_parts:
        premium = random.choice(expensive_parts)
        premium_cost = round(premium["price_range"][1] * random.uniform(0.8, 1.0), 2)
        claim["parts_list"].append(premium["name"])
        claim["parts_cost_claimed"] += premium_cost
        claim["total_claim_amount"] += premium_cost
        claim["text"] += f" Additionally replaced: {premium['name']} (${premium_cost:.2f})."


# ── Utility functions ────────────────────────────────────────────────────

def _random_date(days_back: int = 730) -> date:
    return date.today() - timedelta(days=random.randint(0, days_back))


def _generic_symptoms(category: str) -> list[str]:
    """Generate generic symptoms based on repair category."""
    symptom_map = {
        "Engine": ["Check engine light on", "Engine running rough", "Loss of power", "Strange engine noise", "Poor fuel economy"],
        "Brakes": ["Grinding noise when braking", "Brake pedal pulsation", "Squealing from brakes", "Longer stopping distance", "Brake warning light on"],
        "Suspension": ["Clunking noise over bumps", "Vehicle pulling to one side", "Rough ride quality", "Uneven tire wear", "Steering wheel vibration"],
        "Electrical": ["Warning lights on dashboard", "Battery keeps dying", "Electrical components not working", "Dimming headlights", "Power windows not working"],
        "HVAC": ["AC not blowing cold", "Heater not working", "Strange smell from vents", "Blower motor not working", "Temperature fluctuating"],
        "Transmission": ["Harsh shifting", "Transmission slipping", "Delayed engagement", "Grinding noise when shifting", "Vehicle won't move in gear"],
        "Exhaust": ["Check engine light", "Loud exhaust", "Sulfur smell", "Failed emissions test", "Rattling under vehicle"],
        "Steering": ["Power steering whine", "Difficulty turning wheel", "Loose steering feel", "Steering wheel off center", "Clunking on turns"],
        "Cooling": ["Engine overheating", "Coolant leak", "Temperature gauge high", "Sweet smell from engine bay", "Heater not producing heat"],
        "Fuel System": ["Engine stalling", "Hard starting", "Fuel smell", "Sputtering on acceleration", "Poor fuel economy"],
        "Diagnostics": ["Check engine light on", "Multiple warning lights", "Vehicle not running right"],
        "Body": ["Exterior component loose", "Part not functioning", "Cosmetic damage"],
    }
    return symptom_map.get(category, ["Vehicle not performing properly", "Check engine light", "Unusual noise"])


def _parts_for_category(category: str) -> list[str]:
    """Get common part names for a repair category."""
    cat_parts = [p["name"] for p in PARTS if p["category"] == category]
    if cat_parts:
        return random.sample(cat_parts, min(3, len(cat_parts)))
    return ["Repair Component"]


# ── Dataset generation ───────────────────────────────────────────────────

def generate_dataset(
    n_legitimate: int = 2100,
    n_fraudulent: int = 900,
    seed: int | None = None,
) -> list[dict]:
    """Generate a balanced synthetic dataset.

    Default split is ~70/30 legitimate/fraudulent, totaling 3000 claims.
    """
    if seed is not None:
        random.seed(seed)

    claims: list[dict] = []

    for _ in range(n_legitimate):
        claims.append(generate_legitimate_claim())

    # Distribute fraud patterns
    fraud_patterns = ["labor_inflation", "unnecessary_parts", "symptom_repair_mismatch",
                      "phantom_repair", "upcoding"]
    for i in range(n_fraudulent):
        pattern = fraud_patterns[i % len(fraud_patterns)]
        claims.append(generate_fraudulent_claim(pattern))

    random.shuffle(claims)
    return claims
