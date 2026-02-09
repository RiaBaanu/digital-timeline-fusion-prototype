from datetime import datetime, timedelta
from collections import defaultdict
from statistics import median


def detect_overlapping_events(events, window_seconds=120):
    """
    Detect overlapping events across devices.

    Args:
        events: List[CanonicalEvent]
        window_seconds: Time window to consider overlap

    Returns:
        List of tuples: (event_a, event_b, time_difference_seconds)
    """
    overlaps = []

    # Only consider events with valid timestamps
    valid_events = [
        e for e in events
        if e.timestamp_valid and e.corrected_timestamp is not None
    ]

    # Convert timestamp strings to datetime once
    for e in valid_events:
        e._dt = datetime.fromisoformat(e.corrected_timestamp)

    for i in range(len(valid_events)):
        for j in range(i + 1, len(valid_events)):
            e1 = valid_events[i]
            e2 = valid_events[j]

            # Different devices, same event type
            if e1.device_id == e2.device_id:
                continue
            if e1.event_type != e2.event_type:
                continue

            diff = abs((e1._dt - e2._dt).total_seconds())

            if diff <= window_seconds:
                overlaps.append((e1, e2, diff))

    return overlaps


def calculate_median_skew(overlaps, reference_device):
    """
    Calculate median clock skew per device.

    Args:
        overlaps: list of (event_a, event_b, diff_seconds)
        reference_device: device ID used as time reference

    Returns:
        dict:
        {
            device_id: {
                "offset_seconds": float,
                "confidence": float,
                "samples": int
            }
        }
    """
    offsets = defaultdict(list)

    for e1, e2, diff in overlaps:
        # Align everything relative to reference device
        if e1.device_id == reference_device:
            offsets[e2.device_id].append(diff)
        elif e2.device_id == reference_device:
            offsets[e1.device_id].append(diff)

    results = {}

    max_samples = max(len(v) for v in offsets.values()) if offsets else 1

    for device_id, values in offsets.items():
        med = median(values)
        confidence = len(values) / max_samples

        results[device_id] = {
            "offset_seconds": med,
            "confidence": round(confidence, 2),
            "samples": len(values)
        }

    return results


def apply_clock_skew(events, skew_results, reference_device):
    for e in events:
        # Skip invalid timestamps
        if not e.timestamp_valid:
            continue

        # Skip reference device
        if e.device_id == reference_device:
            continue

        # Skip if no skew info
        if e.device_id not in skew_results:
            continue

        offset = skew_results[e.device_id]["offset_seconds"]

        # Only adjust if corrected_timestamp is a datetime
        if isinstance(e.corrected_timestamp, str):
            from datetime import datetime
            e.corrected_timestamp = datetime.fromisoformat(e.corrected_timestamp)

        if e.corrected_timestamp is not None:
            e.corrected_timestamp = e.corrected_timestamp - timedelta(seconds=offset)

    return events
