from parsers.iot_parser import IoTCSVParser
from pipeline.event_builder import build_canonical_event

parser = IoTCSVParser("data/raw/iot_logs.csv")
raw_events = parser.parse()

for re in raw_events:
    ce = build_canonical_event(re)
    print(
        f"{ce.device_id} | {ce.corrected_timestamp} | "
        f"valid={ce.timestamp_valid} | error={ce.timestamp_error}"
    )