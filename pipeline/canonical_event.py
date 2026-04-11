from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class CanonicalEvent:
    """
    Standardised internal representation of a processed event
    used throughout the Digital Timeline Fusion pipeline.
    """

    # -----------------------------
    # Required Fields
    # -----------------------------
    event_id: str
    device_id: str
    original_timestamp: str
    event_type: str
    payload: Dict[str, Any]
    provenance_file: str
    provenance_row: int
    sha256_hash: str
    timestamp_valid: bool

    # -----------------------------
    # Optional / Derived Fields
    # -----------------------------
    corrected_timestamp: Optional[str] = None
    timestamp_error: Optional[str] = None
    ground_truth_timestamp: Optional[str] = None
    confidence_score: Optional[float] = None
    cluster_id: Optional[str] = None