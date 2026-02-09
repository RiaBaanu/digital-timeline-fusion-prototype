from datetime import datetime, timezone
import statistics


def _to_datetime(ts):
    """
    Convert a timestamp to a timezone-aware datetime (UTC).
    Accepts datetime or ISO-format string.
    Returns None if conversion is not possible.
    """
    if ts is None:
        return None

    # Already a datetime
    if isinstance(ts, datetime):
        if ts.tzinfo is None:
            return ts.replace(tzinfo=timezone.utc)
        return ts

    # String timestamp
    if isinstance(ts, str):
        try:
            dt = datetime.fromisoformat(ts.replace(" ", "T"))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except ValueError:
            return None

    return None


def compute_timestamp_mae(events):
    """
    Compute Mean Absolute Error (MAE) between corrected timestamps
    and ground-truth timestamps (both treated as UTC).
    """
    errors = []

    for e in events:
        if not e.timestamp_valid:
            continue

        # Convert corrected timestamp
        if isinstance(e.corrected_timestamp, datetime):
            corrected = e.corrected_timestamp
        else:
            try:
                corrected = datetime.fromisoformat(
                    e.corrected_timestamp.replace(" ", "T")
                )
            except Exception:
                continue

        if corrected.tzinfo is None:
            corrected = corrected.replace(tzinfo=timezone.utc)

        # Convert ground truth timestamp
        try:
            gt = datetime.fromisoformat(
                e.ground_truth_timestamp.replace(" ", "T")
            )
        except Exception:
            continue

        if gt.tzinfo is None:
            gt = gt.replace(tzinfo=timezone.utc)

        error = abs((corrected - gt).total_seconds())
        errors.append(error)

    if not errors:
        return None

    return round(statistics.mean(errors), 2)


def compute_ordering_accuracy(events):
    """
    Compute ordering accuracy of the fused timeline.

    Returns:
        float between 0 and 1, or None
    """
    valid_events = []

    for e in events:
        ts = _to_datetime(e.corrected_timestamp)
        if ts is not None:
            valid_events.append(ts)

    if len(valid_events) < 2:
        return None

    correct = 0
    total = 0

    for i in range(len(valid_events) - 1):
        if valid_events[i] <= valid_events[i + 1]:
            correct += 1
        total += 1

    return round(correct / total, 2)
