from parsers.iot_parser import IoTCSVParser
from pipeline.event_builder import build_canonical_event
from pipeline.skew_detector import (
    detect_overlapping_events,
    calculate_median_skew,
    apply_clock_skew
)
from pipeline.fusion_engine import fuse_events
from pipeline.evaluation import (
    compute_timestamp_mae,
    compute_ordering_accuracy
)

# Load data
camera_parser = IoTCSVParser("data/synthetic/iot_camera01.csv")
phone_parser = IoTCSVParser("data/synthetic/iot_phone01_skewed.csv")

events = []

for raw_event in camera_parser.parse():
    ce = build_canonical_event(raw_event)
    if ce is not None:
        events.append(ce)

for raw_event in phone_parser.parse():
    ce = build_canonical_event(raw_event)
    if ce is not None:
        events.append(ce)

print("LOADED EVENTS:", len(events))

# Skew correction
overlaps = detect_overlapping_events(events)
skew = calculate_median_skew(overlaps, reference_device="Camera01")
events = apply_clock_skew(events, skew, reference_device="Camera01")

print("AFTER SKEW:", len(events))

# Fusion
fused = fuse_events(events)
print("AFTER FUSION:", len(fused))

for e in fused:
    print(
        "device:", e.device_id,
        "| corrected:", e.corrected_timestamp,
        "| gt:", getattr(e, "ground_truth_timestamp", None),
        "| valid:", e.timestamp_valid
    )

# Evaluation
mae = compute_timestamp_mae(fused)
ordering = compute_ordering_accuracy(fused)

print("Timestamp MAE (seconds):", mae)
print("Ordering accuracy:", ordering)
