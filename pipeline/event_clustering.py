from datetime import datetime
from typing import List
from pipeline.canonical_event import CanonicalEvent


def cluster_events(events: List[CanonicalEvent], window_seconds: int = 5):
    """
    Cluster events across devices based on temporal proximity and event type.

    Events are grouped if they:
    - Share the same event_type.
    - Occur within a specified time window.

    Args:
        events (List[CanonicalEvent]): List of corrected canonical events.
        window_seconds (int): Maximum allowed time difference for clustering.

    Returns:
        List[List[CanonicalEvent]]: A list of event clusters.
    """

    # Filter valid events
    valid_events = [
        e for e in events
        if e.corrected_timestamp is not None and e.timestamp_valid
    ]

    if not valid_events:
        return []

    # Convert timestamps to datetime objects
    for e in valid_events:
        if isinstance(e.corrected_timestamp, str):
            e._dt = datetime.fromisoformat(
                e.corrected_timestamp.replace("Z", "+00:00")
            )
        else:
            e._dt = e.corrected_timestamp

    # Sort events chronologically
    valid_events.sort(key=lambda x: x._dt)

    clusters = []

    for event in valid_events:
        placed = False

        for cluster in clusters:
            ref_event = cluster[0]

            if (
                event.event_type == ref_event.event_type
                and abs((event._dt - ref_event._dt).total_seconds()) <= window_seconds
            ):
                cluster.append(event)
                placed = True
                break

        if not placed:
            clusters.append([event])

    return clusters