from datetime import datetime
from typing import List
from collections import defaultdict
from pipeline.canonical_event import CanonicalEvent


def fuse_events(events: List[CanonicalEvent]) -> List[CanonicalEvent]:
    """
    Fuse events from multiple devices into a single unified timeline.

    This function:
    1. Filters valid events.
    2. Converts timestamps to datetime objects.
    3. Groups correlated events across devices.
    4. Computes per-event fusion confidence.
    5. Sorts events chronologically.

    Args:
        events (List[CanonicalEvent]): List of corrected canonical events.

    Returns:
        List[CanonicalEvent]: Chronologically ordered fused timeline.
    """

    # ----------------------------------
    # Filter valid events
    # ----------------------------------
    valid_events = [
        e for e in events
        if e.corrected_timestamp is not None
    ]

    if not valid_events:
        return []

    # ----------------------------------
    # Convert timestamps to datetime
    # ----------------------------------
    for e in valid_events:
        if isinstance(e.corrected_timestamp, str):
            e._dt = datetime.fromisoformat(
                e.corrected_timestamp.replace("Z", "+00:00")
            )
        else:
            e._dt = e.corrected_timestamp

    # ----------------------------------
    # Group events by timestamp and type
    # ----------------------------------
    grouped = defaultdict(list)

    for e in valid_events:
        key = (e.corrected_timestamp, e.event_type)
        grouped[key].append(e)

    total_devices = len(set(e.device_id for e in valid_events))

    # ----------------------------------
    # Compute fusion confidence
    # ----------------------------------
    for cluster_id, group in enumerate(grouped.values(), start=1):
        supporting_devices = len(set(e.device_id for e in group))
        confidence = round(supporting_devices / total_devices, 2)

        for e in group:
            e.confidence_score = confidence
            e.cluster_id = f"cluster_{cluster_id:03d}"

    # ----------------------------------
    # Sort fused events chronologically
    # ----------------------------------
    valid_events.sort(key=lambda e: e._dt)

    return valid_events