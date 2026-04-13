"""
Digital Timeline Fusion – Core Pipeline
----------------------------------------
Primary operational workflow:

1. Parse device logs
2. Detect and correct clock skew
3. Fuse events chronologically
4. Compute composite confidence
5. Evaluate system metrics
6. Export results (JSON + SQLite)
"""

import os
import uuid
from collections import defaultdict
from datetime import datetime, timezone

from parsers.iot_parser import IoTCSVParser
from pipeline.event_builder import build_canonical_event
from pipeline.skew_detector import (
    detect_overlapping_events,
    calculate_median_skew,
    apply_clock_skew,
)
from pipeline.fusion_engine import fuse_events
from pipeline.exporter import export_to_json
from pipeline.sqlite_store import save_timeline_to_sqlite
from pipeline.evaluation import (
    compute_timestamp_mae,
    compute_weighted_ordering_accuracy,
)
from pipeline.event_clustering import cluster_events
from pipeline.confidence_model import compute_cluster_confidence


# =========================================================
# Utility: Safe Timestamp Parsing
# =========================================================

def parse_ts(ts):
    if ts is None:
        return None

    if isinstance(ts, datetime):
        return ts if ts.tzinfo else ts.replace(tzinfo=timezone.utc)

    try:
        dt = datetime.fromisoformat(str(ts).replace(" ", "T"))
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except Exception:
        return None


# =========================================================
# Residual Skew (Post-Correction)
# =========================================================

def compute_device_residual_skew(events):
    """
    Computes average residual timestamp error per device
    after skew correction.
    Used as reliability input for confidence scoring.
    """
    device_errors = defaultdict(list)

    for e in events:
        if not e.ground_truth_timestamp or not e.corrected_timestamp:
            continue

        gt = parse_ts(e.ground_truth_timestamp)
        ct = parse_ts(e.corrected_timestamp)

        if not gt or not ct:
            continue

        error = (ct - gt).total_seconds()
        device_errors[e.device_id].append(error)

    return {
        device: sum(errors) / len(errors)
        for device, errors in device_errors.items()
        if errors
    }


# =========================================================
# Core Pipeline Execution
# =========================================================

def run():

    os.makedirs("output", exist_ok=True)

    # -----------------------------------------------------
    # 1️⃣ Load & Parse Raw Events
    # -----------------------------------------------------
    parsers = [
        IoTCSVParser("data/synthetic/iot_camera01.csv"),
        IoTCSVParser("data/synthetic/iot_phone01_skewed.csv"),
        IoTCSVParser("data/synthetic/iot_laptop01_skewed.csv"),
        IoTCSVParser("data/synthetic/iot_laptop02_skewed.csv"),
    ]

    raw_events = []
    for parser in parsers:
        raw_events.extend(parser.parse())

    # FIXED: no double build call
    events = [build_canonical_event(e) for e in raw_events]

    total_loaded = len(events)

    # -----------------------------------------------------
    # 2️⃣ Clock Skew Detection & Correction
    # -----------------------------------------------------
    overlaps = detect_overlapping_events(events, reference_device="Camera01")
    skew = calculate_median_skew(overlaps, reference_device="Camera01")
    corrected = apply_clock_skew(events, skew, reference_device="Camera01")

    # -----------------------------------------------------
    # 3️⃣ Chronological Fusion (Confidence Weighted)
    # -----------------------------------------------------
    fused = fuse_events(corrected, confidence_weighted=True)

    # -----------------------------------------------------
    # 4️⃣ Residual Skew (Post-Correction)
    # -----------------------------------------------------
    residuals = compute_device_residual_skew(fused)

    # -----------------------------------------------------
    # 5️⃣ Clustering + Composite Confidence
    # -----------------------------------------------------
    clusters = cluster_events(fused, window_seconds=5)
    total_devices = len({e.device_id for e in fused})

    for cluster in clusters:

        composite_confidence = compute_cluster_confidence(
            cluster,
            residuals,
            total_devices,
        )

        cluster_id = str(uuid.uuid4())

        for e in cluster:
            e.confidence_score = composite_confidence
            e.cluster_id = cluster_id

    # -----------------------------------------------------
    # 6️⃣ Evaluation Metrics
    # -----------------------------------------------------
    mae = compute_timestamp_mae(fused)
    weighted_ordering = compute_weighted_ordering_accuracy(fused)

    # -----------------------------------------------------
    # 7️⃣ Export Results
    # -----------------------------------------------------
    export_to_json(fused, "output/fused_timeline.json")
    save_timeline_to_sqlite(fused, "output/fused_timeline.db")

    # -----------------------------------------------------
    # 8️⃣ Final Summary
    # -----------------------------------------------------
    print("\nDigital Timeline Fusion – Summary")
    print("----------------------------------")
    print(f"Total events processed  : {total_loaded}")
    print(f"Fused events            : {len(fused)}")
    print(f"Overlapping pairs       : {len(overlaps)}")

    if mae is not None:
        print(f"Timestamp MAE (sec)     : {mae:.4f}")
    else:
        print("Timestamp MAE (sec)     : N/A")

    if weighted_ordering is not None:
        print(f"Weighted ordering score : {weighted_ordering:.4f}")
    else:
        print("Weighted ordering score : N/A")

    print("Output saved to: output/fused_timeline.json / output/fused_timeline.db\n")


if __name__ == "__main__":
    run()
