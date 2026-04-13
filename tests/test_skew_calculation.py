from parsers.iot_parser import IoTCSVParser
from pipeline.event_builder import build_canonical_event
from pipeline.skew_detector import detect_overlapping_events, calculate_median_skew

camera_parser = IoTCSVParser("data/synthetic/iot_camera01.csv")
phone_parser = IoTCSVParser("data/synthetic/iot_phone01_skewed.csv")

events = []

for re in camera_parser.parse():
    events.append(build_canonical_event(re))

for re in phone_parser.parse():
    events.append(build_canonical_event(re))


overlaps = detect_overlapping_events(
    events,
    reference_device="Camera01"
)

results = calculate_median_skew(overlaps, reference_device="Camera01")

print(results)
