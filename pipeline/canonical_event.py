from dataclasses import dataclass
from typing import Optional


@dataclass
class CanonicalEvent:
    event_id: str
    device_id: str
    original_timestamp: str
    corrected_timestamp: str | None
    event_type: str
    payload: dict
    provenance_file: str
    provenance_row: int
    sha256_hash: str
    confidence_score: float | None

    # flags
    timestamp_valid: bool
    timestamp_error: str | None

    # ADD THIS
    ground_truth_timestamp: Optional[str] = None
