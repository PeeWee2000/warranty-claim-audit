"""Decomposed claim component schemas.

A raw claim is broken down into these semantic components so that each
can be independently embedded, searched, and scored.
"""

from pydantic import BaseModel, Field


class SymptomComponent(BaseModel):
    """Customer-reported symptoms and complaints."""

    description: str = Field(..., description="Extracted symptom text")
    keywords: list[str] = Field(default_factory=list, description="Key symptom terms")


class DiagnosisComponent(BaseModel):
    """Technician diagnostic findings."""

    description: str = Field(..., description="Extracted diagnosis text")
    fault_codes: list[str] = Field(
        default_factory=list, description="Any DTC or fault codes mentioned"
    )


class PartItem(BaseModel):
    """A single part referenced in the claim."""

    name: str
    part_number: str | None = None
    quantity: int = 1
    unit_cost: float | None = None


class PartsComponent(BaseModel):
    """Parts proposed for replacement."""

    parts: list[PartItem] = Field(default_factory=list)
    total_parts_cost: float | None = None


class LaborComponent(BaseModel):
    """Labor estimate details."""

    description: str | None = Field(
        default=None, description="Description of work to be performed"
    )
    hours_claimed: float = Field(..., ge=0, description="Labor hours requested")
    book_time_hours: float | None = Field(
        default=None, ge=0, description="Standard book time for this repair"
    )
    labor_rate: float | None = Field(
        default=None, ge=0, description="Hourly labor rate"
    )


class VehicleContext(BaseModel):
    """Vehicle information relevant to claim evaluation."""

    make: str | None = None
    model: str | None = None
    year: int | None = None
    mileage: int | None = None
    warranty_start_date: str | None = None
    warranty_end_date: str | None = None


class VerbatimComponent(BaseModel):
    """Raw customer language, preserved for semantic analysis."""

    text: str = Field(..., description="Unmodified customer verbatim")


class ClaimComponents(BaseModel):
    """A fully decomposed claim with all semantic components extracted."""

    symptom: SymptomComponent | None = None
    diagnosis: DiagnosisComponent | None = None
    parts: PartsComponent | None = None
    labor: LaborComponent | None = None
    vehicle: VehicleContext | None = None
    verbatim: VerbatimComponent | None = None

    @property
    def available_components(self) -> list[str]:
        """Return names of components that were successfully extracted."""
        return [
            name
            for name in ["symptom", "diagnosis", "parts", "labor", "vehicle", "verbatim"]
            if getattr(self, name) is not None
        ]
