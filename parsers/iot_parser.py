# parsers/iot_parser.py

import csv
import hashlib
from typing import List
from parsers.base_parser import BaseParser
from pipeline.raw_event import RawEvent


def compute_sha256(file_path: str) -> str:
    """
    Compute SHA-256 hash of a file for forensic integrity validation.
    """
    hash_obj = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_obj.update(chunk)
    return hash_obj.hexdigest()


class IoTCSVParser(BaseParser):
    """
    Parser for IoT CSV event logs.

    Expected columns:
        - timestamp
        - ground_truth_timestamp (optional)
        - device_id
        - event_type
        - value
    """

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.file_hash = compute_sha256(file_path)

    def parse(self) -> List[RawEvent]:
        """
        Parse CSV file into a list of RawEvent objects.
        """

        events = []

        with open(self.file_path, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)

            for idx, row in enumerate(reader, start=1):

                # Skip completely empty rows
                if not any(row.values()):
                    continue

                event = RawEvent(
                    raw_timestamp=(row.get("timestamp") or "").strip() or None,
                    ground_truth_timestamp=(row.get("ground_truth_timestamp") or "").strip() or None,
                    device_id=(row.get("device_id") or "").strip(),
                    event_type=(row.get("event_type") or "").strip(),
                    payload={
                        "value": row.get("value")
                    },
                    provenance_file=self.file_path,
                    provenance_row=idx,
                    sha256_hash=self.file_hash
                )

                events.append(event)

        return events