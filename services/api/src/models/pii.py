"""PII-related schemas.

These define the data structures for PII detection and redaction.
Implementation is deferred — only the schema contracts are defined here.
"""

from enum import Enum

from pydantic import BaseModel, Field


class PIIType(str, Enum):
    """Categories of PII that the redactor can detect."""

    PERSON_NAME = "person_name"
    VIN = "vin"
    PHONE = "phone"
    EMAIL = "email"
    ADDRESS = "address"
    DEALER_ID = "dealer_id"
    SSN = "ssn"
    LICENSE_PLATE = "license_plate"


class PIIEntity(BaseModel):
    """A single detected PII entity."""

    entity_type: PIIType
    start: int = Field(..., description="Character offset start in original text")
    end: int = Field(..., description="Character offset end in original text")
    text: str = Field(..., description="The detected PII text")
    confidence: float = Field(..., ge=0.0, le=1.0)
    replacement: str = Field(
        default="[REDACTED]",
        description="Placeholder text used in the redacted output",
    )


class PIIRedactionResult(BaseModel):
    """Result of running PII redaction on claim text."""

    original_length: int
    redacted_text: str = Field(..., description="Text with PII replaced by placeholders")
    entities_found: list[PIIEntity] = Field(default_factory=list)
    entity_count: int = 0
