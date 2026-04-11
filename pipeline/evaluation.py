from datetime import datetime, timezone
import statistics


def _to_utc_datetime(ts):
    """
    Safely convert timestamp (string or datetime) to UTC datetime.
    Returns None if invalid.
    """

    if ts is None:
        return None

    if isinstance(ts, datetime):
        if ts.tzinfo is None:
            return ts.replace(tzinfo=timezone.utc)
        return ts

    if isinstance(ts, str):
        try:
            dt = datetime.fromisoformat(ts.replace(" ", "T"))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except Exception:
            return None

    return None


def compute_timestamp_mae(events):
    """
    Compute Mean Absolute Error (MAE) between corrected timestamps
    and ground-truth timestamps.
    """

    errors = []

    for e in events:
        if not e.timestamp_valid:
            continue

        corrected = _to_utc_datetime(e.corrected_timestamp)
        ground_truth = _to_utc_datetime(e.ground_truth_timestamp)

        if corrected is None or ground_truth is None:
            continue

        error = abs((corrected - ground_truth).total_seconds())
        errors.append(error)

    if not errors:
        return None

    return round(statistics.mean(errors), 2)


def compute_ordering_accuracy(events):
    """
    Compute chronological ordering accuracy of fused timeline.
    Returns float between 0 and 1.
    """

    valid_events = []

    for e in events:
        dt = _to_utc_datetime(e.corrected_timestamp)
        if dt is not None:
            valid_events.append((dt, e.event_id))

    if len(valid_events) < 2:
        return None

    valid_events.sort(key=lambda x: x[0])

    correct = 0
    total = len(valid_events) - 1

    for i in range(total):
        if valid_events[i][0] <= valid_events[i + 1][0]:
            correct += 1

    return round(correct / total, 2)