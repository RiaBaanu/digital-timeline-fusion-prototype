import uuid
import logging
from pipeline.raw_event import RawEvent
from pipeline.canonical_event import CanonicalEvent
from pipeline.normaliser import normalise_to_utc


def build_canonical_event(raw_event: RawEvent) -> CanonicalEvent:
    """
    Transform RawEvent into CanonicalEvent with UTC normalisation
    and validation flags.
    """

    utc_timestamp, error = normalise_to_utc(raw_event.raw_timestamp)

    if error == "malformed_timestamp":
        logging.warning(
            f"Malformed timestamp in {raw_event.provenance_file}, "
            f"row {raw_event.provenance_row}: {raw_event.raw_timestamp}"
        )

    return CanonicalEvent(
        event_id=str(uuid.uuid4()),
        device_id=raw_event.device_id,
        original_timestamp=raw_event.raw_timestamp,
        corrected_timestamp=utc_timestamp,
        ground_truth_timestamp=raw_event.ground_truth_timestamp,
        event_type=raw_event.event_type,
        payload=raw_event.payload,
        provenance_file=raw_event.provenance_file,
        provenance_row=raw_event.provenance_row,
        sha256_hash=raw_event.sha256_hash,
        confidence_score=None,
        timestamp_valid=(error is None),
        timestamp_error=error
    )