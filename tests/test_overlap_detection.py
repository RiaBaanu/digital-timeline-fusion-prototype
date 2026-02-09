from parsers.iot_parser import IoTCSVParser
from pipeline.event_builder import build_canonical_event
from pipeline.skew_detector import detect_overlapping_events

# Load both devices
camera_parser = IoTCSVParser("data/synthetic/iot_camera01.csv")
phone_parser = IoTCSVParser("data/synthetic/iot_phone01_skewed.csv")

events = []

for re in camera_parser.parse():
    events.append(build_canonical_event(re))

for re in phone_parser.parse():
    events.append(build_canonical_event(re))

overlaps = detect_overlapping_events(events)

print(f"Found {len(overlaps)} overlapping event pairs")

for e1, e2, diff in overlaps:
    print(
        e1.device_id,
        e2.device_id,
        diff
    )
