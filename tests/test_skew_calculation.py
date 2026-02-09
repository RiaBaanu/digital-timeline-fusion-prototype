from parsers.iot_parser import IoTCSVParser
from pipeline.event_builder import build_canonical_event
from pipeline.skew_detector import detect_overlapping_events, calculate_median_skew

camera_parser = IoTCSVParser("data/synthetic/iot_camera01.csv")
phone_parser = IoTCSVParser("data/synthetic/iot_phone01_skewed.csv")

events = []

for re in camera_parser.parse():
    ce = build_canonical_event(re)
if ce is not None:
    events.append(ce)


for re in phone_parser.parse():
    ce = build_canonical_event(re)
if ce is not None:
    events.append(ce)


overlaps = detect_overlapping_events(events)

results = calculate_median_skew(overlaps, reference_device="Camera01")

print(results)
