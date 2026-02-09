from parsers.iot_parser import IoTCSVParser
from pipeline.event_builder import build_canonical_event

parser = IoTCSVParser("data/raw/iot_logs.csv")
raw_events = parser.parse()

for re in raw_events:
    ce = build_canonical_event(re)
    print(
        ce.corrected_timestamp,
        ce.timestamp_valid,
        ce.timestamp_error
    )
