"""Core claim input schemas."""

from datetime import date
from enum import Enum

from pydantic import BaseModel, Field


class ClaimType(str, Enum):
    WARRANTY = "warranty"
    GOODWILL = "goodwill"
    RECALL = "recall"
    EXTENDED = "extended_warranty"


class ClaimMetadata(BaseModel):
    """Structured metadata extracted from or submitted with a claim."""

    claim_id: str | None = Field(default=None, description="External claim identifier")
    claim_date: date | None = Field(default=None, description="Date the claim was filed")
    claim_type: ClaimType = Field(default=ClaimType.WARRANTY)
    dealer_code: str | None = Field(default=None, description="Dealer identifier")
    region: str | None = Field(default=None, description="Geographic region")


class RawClaim(BaseModel):
    """A raw warranty claim as received for scoring.

    This is the primary input to the system. It may contain unstructured text,
    structured fields, or a mix of both.
    """

    text: str = Field(
        ...,
        min_length=10,
        description="The full claim text, including symptom, diagnosis, and repair details",
    )
    metadata: ClaimMetadata = Field(default_factory=ClaimMetadata)

    # Optional pre-parsed structured fields that supplement the free text.
    vehicle_make: str | None = Field(default=None, examples=["Ford", "Toyota", "BMW"])
    vehicle_model: str | None = Field(default=None, examples=["F-150", "Camry", "X5"])
    vehicle_year: int | None = Field(default=None, ge=1990, le=2030)
    vehicle_mileage: int | None = Field(default=None, ge=0)
    labor_hours_claimed: float | None = Field(default=None, ge=0)
    parts_cost_claimed: float | None = Field(default=None, ge=0)
    total_claim_amount: float | None = Field(default=None, ge=0)
