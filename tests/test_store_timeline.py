from parsers.iot_parser import IoTCSVParser
from pipeline.event_builder import build_canonical_event
from pipeline.skew_detector import (
    detect_overlapping_events,
    calculate_median_skew,
    apply_clock_skew
)
from pipeline.fusion_engine import fuse_events
from pipeline.exporter import export_to_json


# Load data
camera_parser = IoTCSVParser("data/synthetic/iot_camera01.csv")
phone_parser = IoTCSVParser("data/synthetic/iot_phone01_skewed.csv")

events = []

for row in camera_parser.parse():
    events.append(build_canonical_event(row))

for row in phone_parser.parse():
    events.append(build_canonical_event(row))

# Skew correction
overlaps = detect_overlapping_events(events)
skew = calculate_median_skew(overlaps, reference_device="Camera01")
events = apply_clock_skew(events, skew, reference_device="Camera01")

# Fusion
fused = fuse_events(events)

# Save output
output_path = "data/synthetic/fused_timeline.json"
export_to_json(fused, output_path)

print(f"Fused timeline saved to {output_path}")
