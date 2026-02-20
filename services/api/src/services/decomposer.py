"""Claim component decomposer.

Takes raw claim text and extracts structured semantic components:
symptom, diagnosis, parts, labor, vehicle context, and verbatim.

This implementation uses regex and keyword-based heuristics for extraction.
A future iteration could use a fine-tuned NER model or LLM-based extraction.
"""

import re

from ..models.components import (
    ClaimComponents,
    DiagnosisComponent,
    LaborComponent,
    PartItem,
    PartsComponent,
    SymptomComponent,
    VehicleContext,
    VerbatimComponent,
)
from ..models.claim import RawClaim

# Keyword lists for section classification
_SYMPTOM_KEYWORDS = [
    "customer states", "customer reports", "complaint", "concern",
    "noise", "vibration", "leak", "warning light", "check engine",
    "squealing", "grinding", "pulling", "stalling", "overheating",
    "smell", "smoke", "rough idle", "misfire", "shaking",
]

_DIAGNOSIS_KEYWORDS = [
    "found", "diagnosed", "inspection", "tested", "confirmed",
    "measured", "fault code", "dtc", "root cause", "worn",
    "cracked", "failed", "defective", "out of spec", "corroded",
]

_LABOR_PATTERN = re.compile(
    r"(\d+\.?\d*)\s*(?:hours?|hrs?|hr)\b", re.IGNORECASE
)

_BOOK_TIME_PATTERN = re.compile(
    r"book\s*time[:\s]*(\d+\.?\d*)\s*(?:hours?|hrs?|hr)?", re.IGNORECASE
)

_LABOR_RATE_PATTERN = re.compile(
    r"\$(\d+\.?\d*)\s*/?\s*(?:hour|hr)\b", re.IGNORECASE
)

_VEHICLE_YEAR_PATTERN = re.compile(
    r"\b((?:19|20)\d{2})\b"
)

_MILEAGE_PATTERN = re.compile(
    r"(\d{1,3}(?:,\d{3})*)\s*(?:miles|mi)\b", re.IGNORECASE
)

_COMMON_MAKES = [
    "Ford", "Chevrolet", "Chevy", "Toyota", "Honda", "BMW", "Mercedes",
    "Dodge", "Ram", "Jeep", "GMC", "Nissan", "Hyundai", "Kia",
    "Subaru", "Volkswagen", "VW", "Audi", "Lexus", "Mazda", "Volvo",
    "Chrysler", "Buick", "Cadillac", "Lincoln", "Acura", "Infiniti",
]

_COMMON_MODELS = [
    "F-150", "F150", "Silverado", "Camry", "Civic", "Accord", "Corolla",
    "RAV4", "CR-V", "X5", "X3", "3 Series", "C-Class", "Wrangler",
    "Grand Cherokee", "Sierra", "Altima", "Sentra", "Elantra", "Tucson",
    "Optima", "Outback", "Forester", "Jetta", "Golf", "A4", "Q5",
    "Mustang", "Explorer", "Escape", "Edge", "Ranger", "Tacoma",
    "Tundra", "Highlander", "Pilot", "Odyssey", "Camaro", "Malibu",
    "Equinox", "Traverse", "Tahoe", "Suburban",
]


def _score_sentence(sentence: str, keywords: list[str]) -> int:
    """Count how many keywords appear in a sentence."""
    lower = sentence.lower()
    return sum(1 for kw in keywords if kw in lower)


def _split_sentences(text: str) -> list[str]:
    """Split text into sentences, preserving meaningful chunks."""
    parts = re.split(r'(?<=[.!?])\s+|\n+', text)
    return [s.strip() for s in parts if s.strip()]


def _extract_vehicle(text: str, claim: RawClaim) -> VehicleContext | None:
    """Extract vehicle information from text and structured fields."""
    make = claim.vehicle_make
    model = claim.vehicle_model
    year = claim.vehicle_year
    mileage = claim.vehicle_mileage

    if not make:
        for m in _COMMON_MAKES:
            if re.search(rf"\b{re.escape(m)}\b", text, re.IGNORECASE):
                make = m
                break

    if not model:
        for m in _COMMON_MODELS:
            if re.search(rf"\b{re.escape(m)}\b", text, re.IGNORECASE):
                model = m
                break

    if not year:
        match = _VEHICLE_YEAR_PATTERN.search(text)
        if match:
            year = int(match.group(1))

    if not mileage:
        match = _MILEAGE_PATTERN.search(text)
        if match:
            mileage = int(match.group(1).replace(",", ""))

    if any([make, model, year, mileage]):
        return VehicleContext(make=make, model=model, year=year, mileage=mileage)
    return None


def _extract_labor(text: str, claim: RawClaim) -> LaborComponent | None:
    """Extract labor details from text and structured fields."""
    hours = claim.labor_hours_claimed
    if not hours:
        match = _LABOR_PATTERN.search(text)
        if match:
            hours = float(match.group(1))

    if hours is None:
        return None

    book_time = None
    match = _BOOK_TIME_PATTERN.search(text)
    if match:
        book_time = float(match.group(1))

    rate = None
    match = _LABOR_RATE_PATTERN.search(text)
    if match:
        rate = float(match.group(1))

    # Try to find a labor description sentence
    description = None
    for sentence in _split_sentences(text):
        lower = sentence.lower()
        if any(w in lower for w in ["replace", "repair", "install", "remove", "r&r"]):
            description = sentence
            break

    return LaborComponent(
        description=description,
        hours_claimed=hours,
        book_time_hours=book_time,
        labor_rate=rate,
    )


def _extract_parts(text: str, claim: RawClaim) -> PartsComponent | None:
    """Extract parts information from text."""
    # Look for part-number-like patterns (e.g., "PN 12345", "part# AB-1234")
    part_patterns = re.findall(
        r"(?:part\s*#?|pn|p/n)[:\s]*([A-Z0-9][\w-]{3,})",
        text,
        re.IGNORECASE,
    )

    # Look for common part names
    common_parts = [
        "brake pad", "rotor", "caliper", "strut", "shock", "control arm",
        "tie rod", "ball joint", "wheel bearing", "cv axle", "cv joint",
        "alternator", "starter", "battery", "water pump", "thermostat",
        "radiator", "spark plug", "ignition coil", "fuel pump", "fuel injector",
        "oxygen sensor", "o2 sensor", "catalytic converter", "muffler",
        "transmission", "clutch", "flywheel", "timing belt", "timing chain",
        "serpentine belt", "power steering pump", "ac compressor",
    ]

    found_parts: list[PartItem] = []
    text_lower = text.lower()

    for part_name in common_parts:
        if part_name in text_lower:
            pn = None
            if part_patterns:
                pn = part_patterns.pop(0)
            found_parts.append(PartItem(name=part_name.title(), part_number=pn))

    # If we found part numbers but no named parts, create entries from numbers
    for remaining_pn in part_patterns:
        found_parts.append(PartItem(name="Unknown Part", part_number=remaining_pn))

    if not found_parts:
        return None

    return PartsComponent(
        parts=found_parts,
        total_parts_cost=claim.parts_cost_claimed,
    )


def decompose(claim: RawClaim) -> ClaimComponents:
    """Decompose a raw claim into semantic components.

    Args:
        claim: The raw claim input with text and optional structured fields.

    Returns:
        ClaimComponents with each extracted component populated where possible.
    """
    text = claim.text
    sentences = _split_sentences(text)

    # Classify sentences into symptom vs diagnosis buckets
    symptom_sentences: list[str] = []
    diagnosis_sentences: list[str] = []
    other_sentences: list[str] = []

    for sentence in sentences:
        symptom_score = _score_sentence(sentence, _SYMPTOM_KEYWORDS)
        diagnosis_score = _score_sentence(sentence, _DIAGNOSIS_KEYWORDS)

        if symptom_score > diagnosis_score:
            symptom_sentences.append(sentence)
        elif diagnosis_score > symptom_score:
            diagnosis_sentences.append(sentence)
        else:
            other_sentences.append(sentence)

    # Build symptom component
    symptom = None
    if symptom_sentences:
        symptom_text = " ".join(symptom_sentences)
        keywords = [
            kw for kw in _SYMPTOM_KEYWORDS if kw in symptom_text.lower()
        ]
        symptom = SymptomComponent(description=symptom_text, keywords=keywords)

    # Build diagnosis component
    diagnosis = None
    if diagnosis_sentences:
        diag_text = " ".join(diagnosis_sentences)
        fault_codes = re.findall(r"\b[A-Z]\d{4}\b", text)  # e.g., P0301, B1234
        diagnosis = DiagnosisComponent(description=diag_text, fault_codes=fault_codes)

    # Build other components
    vehicle = _extract_vehicle(text, claim)
    labor = _extract_labor(text, claim)
    parts = _extract_parts(text, claim)

    # Verbatim: preserve the full original text
    verbatim = VerbatimComponent(text=text)

    return ClaimComponents(
        symptom=symptom,
        diagnosis=diagnosis,
        parts=parts,
        labor=labor,
        vehicle=vehicle,
        verbatim=verbatim,
    )
