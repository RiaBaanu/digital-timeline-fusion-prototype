import json
from datetime import datetime
from typing import List
from pipeline.canonical_event import CanonicalEvent


def _serialize_timestamp(ts):
    """
    Convert datetime objects to ISO 8601 format for JSON serialization.
    """
    if ts is None:
        return None
    if isinstance(ts, datetime):
        return ts.isoformat()
    return str(ts)


def export_to_json(events: List[CanonicalEvent], output_path: str) -> str:
    """
    Export fused timeline events to a structured JSON file.

    Args:
        events (List[CanonicalEvent]): List of fused events.
        output_path (str): Path to the output JSON file.

    Returns:
        str: Path to the generated JSON file.
    """

    serialized = []

    for e in events:
        serialized.append({
            "event_id": e.event_id,
            "cluster_id": getattr(e, "cluster_id", None),
            "device_id": e.device_id,
            "original_timestamp": e.original_timestamp,
            "corrected_timestamp": _serialize_timestamp(e.corrected_timestamp),
            "event_type": e.event_type,
            "payload": e.payload,
            "provenance_file": e.provenance_file,
            "provenance_row": e.provenance_row,
            "sha256_hash": e.sha256_hash,
            "confidence_score": e.confidence_score,
            "timestamp_valid": e.timestamp_valid,
            "timestamp_error": e.timestamp_error
        })

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(serialized, f, indent=4)

    print(f"Fused timeline exported to {output_path}")
    return output_path