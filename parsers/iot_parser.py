# parsers/iot_parser.py
import csv
from typing import List
from parsers.base_parser import BaseParser
from pipeline.raw_event import RawEvent
from pipeline.provenance import compute_sha256


class IoTCSVParser(BaseParser):

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.file_hash = compute_sha256(file_path)

    def parse(self) -> List[RawEvent]:
        events = []

        with open(self.file_path, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)

            for idx, row in enumerate(reader):
                event = RawEvent(
                    raw_timestamp=row.get("timestamp") or None,
                    ground_truth_timestamp=row.get("ground_truth_timestamp") or None,
                    device_id=row.get("device_id") or "",
                    event_type=row.get("event_type") or "",
                    payload={"value": row.get("value")},
                    provenance_file=self.file_path,
                    provenance_row=idx,
                    sha256_hash=self.file_hash
                )

                events.append(event)

        return events
