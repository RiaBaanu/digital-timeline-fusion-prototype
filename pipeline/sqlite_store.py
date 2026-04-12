import sqlite3
from dataclasses import asdict


def save_timeline_to_sqlite(events, db_path):
    """
    Save fused timeline events into a SQLite database.

    Args:
        events (List[CanonicalEvent]): List of fused events.
        db_path (str): Path to SQLite database file.
    """

    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()

        # --------------------------------------------------
        # Create Table (if not exists)
        # --------------------------------------------------
        cur.execute("""
            CREATE TABLE IF NOT EXISTS timeline (
                event_id TEXT PRIMARY KEY,
                cluster_id TEXT,
                device_id TEXT,
                original_timestamp TEXT,
                corrected_timestamp TEXT,
                ground_truth_timestamp TEXT,
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

        # --------------------------------------------------
        # Clear Old Data
        # --------------------------------------------------
        cur.execute("DELETE FROM timeline")

        # --------------------------------------------------
        # Insert Events
        # --------------------------------------------------
        for e in events:
            data = asdict(e)

            cur.execute("""
                INSERT OR REPLACE INTO timeline (
                    event_id,
                    cluster_id,
                    device_id,
                    original_timestamp,
                    corrected_timestamp,
                    ground_truth_timestamp,
                    event_type,
                    payload,
                    provenance_file,
                    provenance_row,
                    sha256_hash,
                    confidence_score,
                    timestamp_valid,
                    timestamp_error
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data.get("event_id"),
                data.get("cluster_id"),
                data.get("device_id"),
                data.get("original_timestamp"),
                data.get("corrected_timestamp"),
                data.get("ground_truth_timestamp"),
                data.get("event_type"),
                str(data.get("payload")),
                data.get("provenance_file"),
                data.get("provenance_row"),
                data.get("sha256_hash"),
                data.get("confidence_score"),
                int(data.get("timestamp_valid", 0)),
                data.get("timestamp_error")
            ))

        conn.commit()