"""
Digital Timeline Fusion – Core Evaluation Utilities
---------------------------------------------------
Minimal reusable metrics used by:
- run_pipeline.py
- run_experiments.py
"""

from datetime import datetime, timezone
from statistics import mean


# =========================================================
# Timestamp Parsing
# =========================================================

def parse_ts(ts):
    """
    Safely parses ISO timestamp strings into UTC-aware datetime.
    """
    if ts is None:
        return None

    if isinstance(ts, datetime):
        return ts if ts.tzinfo else ts.replace(tzinfo=timezone.utc)

    if isinstance(ts, str):
        dt = datetime.fromisoformat(ts)
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)

    return None


# =========================================================
# Mean Absolute Error (MAE)
# =========================================================

def compute_mae(events, use_corrected=True):
    """
    Computes Mean Absolute Error against ground truth timestamps.
    """

    errors = []

    for e in events:

        original = parse_ts(e.original_timestamp)
        corrected = parse_ts(e.corrected_timestamp)
        ground_truth = parse_ts(e.ground_truth_timestamp)

        if ground_truth is None:
            continue

        compare = corrected if use_corrected else original

        if compare is None:
            continue

        error = abs((compare - ground_truth).total_seconds())
        errors.append(error)

    return mean(errors) if errors else 0
