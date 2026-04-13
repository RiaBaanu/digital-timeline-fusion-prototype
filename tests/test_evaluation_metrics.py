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

camera_parser = IoTCSVParser("data/synthetic/iot_camera01.csv")
phone_parser = IoTCSVParser("data/synthetic/iot_phone01_skewed.csv")

events = []

for raw_event in camera_parser.parse():
    events.append(build_canonical_event(raw_event))

for raw_event in phone_parser.parse():
    events.append(build_canonical_event(raw_event))

print("LOADED EVENTS:", len(events))

overlaps = detect_overlapping_events(events, reference_device="Camera01")
skew = calculate_median_skew(overlaps, reference_device="Camera01")
events = apply_clock_skew(events, skew, reference_device="Camera01")

fused = fuse_events(events)

mae = compute_timestamp_mae(fused)
ordering = compute_ordering_accuracy(fused)

print("Timestamp MAE (seconds):", mae)
print("Ordering accuracy:", ordering)