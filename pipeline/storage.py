import json
from dataclasses import asdict


def save_timeline_to_json(events, output_path):
    """
    Save fused timeline events to a JSON file.

    Args:
        events: List[CanonicalEvent]
        output_path: Path to output JSON file
    """
    serialised_events = []

    for e in events:
        serialised_events.append(asdict(e))

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(serialised_events, f, indent=2)

    return output_path
