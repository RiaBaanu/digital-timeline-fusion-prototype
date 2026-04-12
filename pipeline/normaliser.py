from datetime import timezone
from dateutil import parser


def normalise_to_utc(timestamp_str: str | None):
    """
    Normalises timestamp string to UTC ISO format.

    Returns:
        (utc_timestamp_iso, error_message)
    """

    if not timestamp_str or not timestamp_str.strip():
        return None, "missing_timestamp"

    try:
        dt = parser.parse(timestamp_str)

        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)

        return dt.astimezone(timezone.utc).isoformat(), None

    except Exception:
        return None, "malformed_timestamp"