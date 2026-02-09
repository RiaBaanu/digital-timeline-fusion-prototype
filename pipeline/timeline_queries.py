import sqlite3


def get_all_events(db_path):
    """
    Retrieve all events from the fused timeline, ordered by corrected timestamp.
    """
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("""
        SELECT *
        FROM timeline
        ORDER BY
            CASE WHEN corrected_timestamp IS NULL THEN 1 ELSE 0 END,
            corrected_timestamp
    """)

    rows = cur.fetchall()
    conn.close()
    return rows


def get_events_by_device(db_path, device_id):
    """
    Retrieve all events for a specific device.
    """
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("""
        SELECT *
        FROM timeline
        WHERE device_id = ?
        ORDER BY
            CASE WHEN corrected_timestamp IS NULL THEN 1 ELSE 0 END,
            corrected_timestamp
    """, (device_id,))

    rows = cur.fetchall()
    conn.close()
    return rows


def get_events_in_time_range(db_path, start_ts, end_ts):
    """
    Retrieve events within a corrected timestamp range.
    """
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("""
        SELECT *
        FROM timeline
        WHERE corrected_timestamp BETWEEN ? AND ?
        ORDER BY corrected_timestamp
    """, (start_ts, end_ts))

    rows = cur.fetchall()
    conn.close()
    return rows
