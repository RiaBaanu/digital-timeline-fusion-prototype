from datetime import datetime


def fuse_events(events):
    """
    Sort events into a single fused timeline.
    Events with invalid timestamps are pushed to the end.
    """

    def sort_key(event):
        if event.corrected_timestamp is None:
            return (1, datetime.max)
        if isinstance(event.corrected_timestamp, str):
            return (0, datetime.fromisoformat(event.corrected_timestamp))
        return (0, event.corrected_timestamp)

    return sorted(events, key=sort_key)
