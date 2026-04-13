"""
forensic_query_interface.py
----------------------------------------
Digital Timeline Fusion – Forensic Query Interface

This script provides an interactive command-line interface (CLI)
for querying and analysing the fused forensic timeline stored in
an SQLite database.

Features:
- Query events by device
- Filter events by confidence score
- Search within a time window
- Analyse event clusters
- Generate dataset summaries

Author: Digital Timeline Fusion Project
"""

import sqlite3
from datetime import datetime

DB_PATH = "output/fused_timeline.db"


# --------------------------------------------------
# Database Utilities
# --------------------------------------------------
def connect_db():
    """Establish a connection to the SQLite database."""
    return sqlite3.connect(DB_PATH)


def get_available_devices():
    """
    Retrieve all unique device IDs from the timeline table.
    Cleans and normalises device names to avoid issues caused by
    whitespace, case differences, or formatting inconsistencies.
    """
    try:
        conn = connect_db()
        cur = conn.cursor()

        cur.execute("""
            SELECT DISTINCT TRIM(device_id)
            FROM timeline
            WHERE device_id IS NOT NULL
            ORDER BY TRIM(device_id)
        """)

        rows = cur.fetchall()
        conn.close()

        # Normalise and remove duplicates
        devices = sorted({row[0].strip() for row in rows if row[0]})

        return devices

    except Exception as e:
        print(f"Error retrieving devices: {e}")
        return []


def get_dataset_time_range():
    """Retrieve the earliest and latest timestamps in the dataset."""
    try:
        with connect_db() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT MIN(corrected_timestamp), MAX(corrected_timestamp) FROM timeline"
            )
            return cur.fetchone()
    except Exception:
        return (None, None)


# --------------------------------------------------
# Helper Functions
# --------------------------------------------------
def classify_confidence(score):
    """Categorise confidence scores."""
    if score >= 0.85:
        return "High"
    elif score >= 0.65:
        return "Medium"
    else:
        return "Low"


def hhmm_to_iso(hhmm, reference_iso):
    """
    Convert HH:MM format into ISO timestamp using the dataset date.
    """
    try:
        ref = datetime.fromisoformat(reference_iso.replace("Z", "+00:00"))
    except Exception:
        ref = datetime.fromisoformat(reference_iso)

    date = ref.date()
    tz = ref.tzinfo

    hours, minutes = map(int, hhmm.split(":"))
    dt = datetime(date.year, date.month, date.day,
                  hours, minutes, 0, tzinfo=tz)
    return dt.isoformat()


# --------------------------------------------------
# Query Functions
# --------------------------------------------------
def query_by_device(device_id):
    """Retrieve events for a specific device."""
    with connect_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT device_id, corrected_timestamp, event_type, confidence_score
            FROM timeline
            WHERE device_id = ?
            ORDER BY corrected_timestamp
        """, (device_id,))
        return cur.fetchall()


def query_by_confidence(min_confidence):
    """Retrieve events above a confidence threshold."""
    with connect_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT device_id, corrected_timestamp, event_type, confidence_score
            FROM timeline
            WHERE confidence_score >= ?
            ORDER BY confidence_score DESC
        """, (min_confidence,))
        return cur.fetchall()


def query_by_time_window(start_time, end_time):
    """Retrieve events within a specific time range."""
    with connect_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT device_id, corrected_timestamp, event_type, confidence_score
            FROM timeline
            WHERE corrected_timestamp BETWEEN ? AND ?
            ORDER BY corrected_timestamp
        """, (start_time, end_time))
        return cur.fetchall()


def query_clusters_by_size(min_devices):
    """Retrieve clusters detected by at least N devices."""
    with connect_db() as conn:
        cur = conn.cursor()

        cur.execute("""
            SELECT cluster_id
            FROM timeline
            WHERE cluster_id IS NOT NULL
            GROUP BY cluster_id
            HAVING COUNT(DISTINCT device_id) >= ?
        """, (min_devices,))

        cluster_ids = [row[0] for row in cur.fetchall()]
        if not cluster_ids:
            return []

        placeholders = ",".join("?" * len(cluster_ids))

        cur.execute(f"""
            SELECT cluster_id, device_id, corrected_timestamp,
                   event_type, confidence_score
            FROM timeline
            WHERE cluster_id IN ({placeholders})
            ORDER BY cluster_id, corrected_timestamp
        """, cluster_ids)

        return cur.fetchall()


def get_dataset_summary():
    """Generate high-level statistics for the dataset."""
    try:
        with connect_db() as conn:
            cur = conn.cursor()

            cur.execute("SELECT COUNT(*) FROM timeline")
            total_events = cur.fetchone()[0]

            cur.execute("""
                SELECT COUNT(DISTINCT cluster_id)
                FROM timeline
                WHERE cluster_id IS NOT NULL
            """)
            total_clusters = cur.fetchone()[0]

            cur.execute("SELECT COUNT(DISTINCT device_id) FROM timeline")
            devices_detected = cur.fetchone()[0]

            cur.execute("""
                SELECT MIN(corrected_timestamp), MAX(corrected_timestamp)
                FROM timeline
            """)
            min_ts, max_ts = cur.fetchone()

            cur.execute("SELECT confidence_score FROM timeline")
            scores = [r[0] for r in cur.fetchall()]

        buckets = {"Low": 0, "Medium": 0, "High": 0, "Unknown": 0}
        for score in scores:
            buckets[classify_confidence(score)] += 1

        return {
            "total_events": total_events,
            "total_clusters": total_clusters,
            "devices_detected": devices_detected,
            "min_ts": min_ts,
            "max_ts": max_ts,
            "confidence_distribution": buckets,
        }
    except Exception:
        return None


# --------------------------------------------------
# CLI Interface
# --------------------------------------------------
def print_results(results):
    """Display query results in a formatted manner."""
    print("\n" + "=" * 65)
    if not results:
        print("No results found.")
    else:
        for row in results:
            device_id, timestamp, event_type, confidence = row
            label = classify_confidence(confidence)

            print(f"\nDevice      : {device_id}")
            print(f"Event       : {event_type}")
            print(f"Timestamp   : {timestamp}")
            print(f"Confidence  : {confidence:.2f} ({label})")
    print("\n" + "=" * 65)


def main():
    """Run the forensic CLI interface."""
    print("\n" + "=" * 65)
    print("       DIGITAL TIMELINE FORENSIC QUERY TOOL")
    print("=" * 65)
    while True:
        devices = get_available_devices()
        min_ts, max_ts = get_dataset_time_range()

        print("\nAvailable Devices:")
        for i, device in enumerate(devices, 1):
            print(f"  {i}. {device}")

        print("\nDataset Time Range:")
        if min_ts and max_ts:
            try:
                dt_min = datetime.fromisoformat(min_ts.replace("Z", "+00:00"))
                dt_max = datetime.fromisoformat(max_ts.replace("Z", "+00:00"))
                print(f"  {dt_min.strftime('%H:%M')} → {dt_max.strftime('%H:%M')}")
            except Exception:
                print("  (Unavailable)")
        else:
            print("  (Unavailable)")

        while True:
            print("\n" + "-" * 65)
            print("MAIN MENU")
            print("-" * 65)
            print("1. Query by device")
            print("2. Query by confidence threshold")
            print("3. Query by time window")
            print("4. Query clusters by minimum device count")
            print("5. Show dataset summary")
            print("6. Exit")

            choice = input("\nSelect option: ").strip()

            if choice == "1":
                try:
                    selection = int(input("Select device number: "))
                    device = devices[selection - 1]
                    print_results(query_by_device(device))
                except (ValueError, IndexError):
                    print("Invalid selection.")

            elif choice == "2":
                try:
                    threshold = float(input("Minimum confidence: "))
                    print_results(query_by_confidence(threshold))
                except ValueError:
                    print("Invalid value.")

            elif choice == "3":
                start = input("Start time (HH:MM): ")
                end = input("End time (HH:MM): ")
                ref_iso = min_ts or datetime.now().isoformat()
                try:
                    start_iso = hhmm_to_iso(start, ref_iso)
                    end_iso = hhmm_to_iso(end, ref_iso)
                    print_results(query_by_time_window(start_iso, end_iso))
                except Exception:
                    print("Invalid time format.")

            elif choice == "4":
                try:
                    min_devices = int(input("Minimum devices: "))
                    print_results(query_clusters_by_size(min_devices))
                except ValueError:
                    print("Invalid number.")

            elif choice == "5":
                summary = get_dataset_summary()
                if summary:
                    print("\nDATASET SUMMARY")
                    print(f"Total events     : {summary['total_events']}")
                    print(f"Total clusters   : {summary['total_clusters']}")
                    print(f"Devices detected : {summary['devices_detected']}")
                    print("\nConfidence Distribution:")
                    for k, v in summary["confidence_distribution"].items():
                        print(f"  {k}: {v}")
                else:
                    print("Unable to retrieve summary.")

            elif choice == "6":
                print("Exiting forensic interface.")
                return

            else:
                print("Invalid option.")

if __name__ == "__main__":
    main()
