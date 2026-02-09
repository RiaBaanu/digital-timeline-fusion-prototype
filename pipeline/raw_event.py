# pipeline/raw_event.py
from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class RawEvent:
    raw_timestamp: str
    ground_truth_timestamp: str
    device_id: str
    event_type: str
    payload: dict
    provenance_file: str
    provenance_row: int
    sha256_hash: str