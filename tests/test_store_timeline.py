from parsers.iot_parser import IoTCSVParser
from pipeline.event_builder import build_canonical_event
from pipeline.skew_detector import (
    detect_overlapping_events,
    calculate_median_skew,
    apply_clock_skew
)
from pipeline.fusion_engine import fuse_events
from pipeline.storage import save_timeline_to_json

# Load data
camera_parser = IoTCSVParser("data/synthetic/iot_camera01.csv")
phone_parser = IoTCSVParser("data/synthetic/iot_phone01_skewed.csv")

events = []

for re in camera_parser.parse():
    events.append(build_canonical_event(re))

for re in phone_parser.parse():
    events.append(build_canonical_event(re))

# Skew correction
overlaps = detect_overlapping_events(events)
skew = calculate_median_skew(overlaps, reference_device="Camera01")
events = apply_clock_skew(events, skew, reference_device="Camera01")

# Fusion
fused = fuse_events(events)

# Save output
output_path = "data/synthetic/fused_timeline.json"
save_timeline_to_json(fused, output_path)

print(f"Fused timeline saved to {output_path}")
