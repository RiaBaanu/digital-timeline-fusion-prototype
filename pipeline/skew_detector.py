from datetime import datetime, timedelta
from collections import defaultdict
from statistics import median, stdev


# =========================================================
# Detect Overlapping Events
# =========================================================

def detect_overlapping_events(events, reference_device=None, window_seconds=120):
    """
    Detect overlapping events between the reference device and other devices
    based on matching event types and timestamps within a tolerance window.
    """
    overlaps = []

    valid_events = [
        e for e in events
        if e.timestamp_valid and e.corrected_timestamp is not None
    ]

    # Convert timestamps to datetime objects
    for e in valid_events:
        e._dt = datetime.fromisoformat(
            str(e.corrected_timestamp).replace("Z", "+00:00")
        )

    reference_events = [
        e for e in valid_events if e.device_id == reference_device
    ]

    other_devices = {
        e.device_id for e in valid_events if e.device_id != reference_device
    }

    for device in other_devices:
        device_events = [
            e for e in valid_events if e.device_id == device
        ]

        for ref_event in reference_events:
            matches = [
                e for e in device_events
                if e.event_type == ref_event.event_type
            ]

            if not matches:
                continue

            target = matches[0]
            diff = abs((ref_event._dt - target._dt).total_seconds())

            if diff <= window_seconds:
                overlaps.append((ref_event, target, diff))

    return overlaps


# =========================================================
# Calculate Median Clock Skew
# =========================================================

def calculate_median_skew(overlaps, reference_device, window_seconds=120):
    """
    Calculate median clock skew for each device relative to the reference.
    Also computes a confidence score based on sample size and stability.
    """
    offsets = defaultdict(list)

    for e1, e2, diff in overlaps:
        if e1.device_id == reference_device:
            offsets[e2.device_id].append(diff)
        elif e2.device_id == reference_device:
            offsets[e1.device_id].append(diff)

    results = {}

    for device_id, values in offsets.items():
        med = median(values)
        samples = len(values)

        # Sample strength factor
        sample_factor = min(samples / 10, 1.0)

        # Stability factor
        spread = stdev(values) if samples > 1 else 0
        stability_factor = 1 - min(spread / window_seconds, 1)

        confidence = round(sample_factor * stability_factor, 2)

        results[device_id] = {
            "offset_seconds": med,
            "confidence": confidence,
            "samples": samples,
            "spread": round(spread, 2),
        }

    return results


# =========================================================
# Apply Clock Skew Correction
# =========================================================

def apply_clock_skew(events, skew_results, reference_device):
    """
    Apply clock skew correction and assign confidence scores to events.
    """
    corrected_events = []

    for e in events:
        # Reference device: no correction
        if e.device_id == reference_device:
            e.confidence_score = 1.0
            corrected_events.append(e)
            continue

        # Invalid timestamps
        if not e.timestamp_valid or e.corrected_timestamp is None:
            e.confidence_score = 0.0
            corrected_events.append(e)
            continue

        # Apply skew correction if available
        if e.device_id in skew_results:
            offset = skew_results[e.device_id]["offset_seconds"]
            confidence = skew_results[e.device_id]["confidence"]

            ts = datetime.fromisoformat(
                str(e.corrected_timestamp).replace("Z", "+00:00")
            )

            corrected_ts = ts - timedelta(seconds=offset)
            e.corrected_timestamp = corrected_ts.isoformat()
            e.confidence_score = confidence
        else:
            # Default confidence for devices without skew estimation
            e.confidence_score = 0.5

        corrected_events.append(e)

    return corrected_events