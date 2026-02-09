from parsers.iot_parser import IoTCSVParser
from pipeline.event_builder import build_canonical_event
from pipeline.skew_detector import (
    detect_overlapping_events,
    calculate_median_skew,
    apply_clock_skew
)
from pipeline.fusion_engine import fuse_events
from pipeline.sqlite_store import save_timeline_to_sqlite

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

# Save to SQLite
db_path = "db/fused_timeline.db"
save_timeline_to_sqlite(fused, db_path)

print(f"Fused timeline stored in {db_path}")
