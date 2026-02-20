"""PII redaction service — stub.

Implementation deferred. This module defines the interface contract only.
"""

from ..models.pii import PIIRedactionResult


def redact(text: str) -> PIIRedactionResult:
    """Placeholder: returns text unmodified.

    A real implementation would use Microsoft Presidio or spaCy NER
    to detect and mask PII entities before downstream processing.
    """
    return PIIRedactionResult(
        original_length=len(text),
        redacted_text=text,
        entities_found=[],
        entity_count=0,
    )
