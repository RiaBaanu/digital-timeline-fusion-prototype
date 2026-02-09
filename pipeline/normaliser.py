from datetime import timezone
from dateutil import parser


def normalise_to_utc(timestamp_str: str | None):
    """
    Returns:
      (utc_timestamp, error_message)
    """
    if timestamp_str is None or timestamp_str.strip() == "":
        return None, "missing_timestamp"

    try:
        dt = parser.parse(timestamp_str)

        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)

        return dt.astimezone(timezone.utc).isoformat(), None

    except Exception:
        return None, "malformed_timestamp"
