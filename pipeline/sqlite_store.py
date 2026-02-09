import sqlite3
from dataclasses import asdict


def save_timeline_to_sqlite(events, db_path):
    """
    Save fused timeline events into a SQLite database.

    Args:
        events: List[CanonicalEvent]
        db_path: Path to SQLite database file
    """
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Create table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS timeline (
            event_id TEXT PRIMARY KEY,
            device_id TEXT,
            original_timestamp TEXT,
            corrected_timestamp TEXT,
            event_type TEXT,
            payload TEXT,
            provenance_file TEXT,
            provenance_row INTEGER,
            sha256_hash TEXT,
            confidence_score REAL,
            timestamp_valid INTEGER,
            timestamp_error TEXT
        )
    """)

    # Insert events
    for e in events:
        data = asdict(e)

        cur.execute("""
            INSERT OR REPLACE INTO timeline VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data["event_id"],
            data["device_id"],
            data["original_timestamp"],
            data["corrected_timestamp"],
            data["event_type"],
            str(data["payload"]),
            data["provenance_file"],
            data["provenance_row"],
            data["sha256_hash"],
            data["confidence_score"],
            int(data["timestamp_valid"]),
            data["timestamp_error"]
        ))

    conn.commit()
    conn.close()
