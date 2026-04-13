"""
Timeline Visualisation Module
--------------------------------
Generates a confidence-coloured timeline plot from the fused SQLite database.
Used for qualitative evaluation of event fusion accuracy.
"""

import os
import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt


# =========================================================
# Confidence Colour Classification
# =========================================================

def classify_color(score):
    """
    Assign colour based on confidence score.
    """
    if score is None:
        return "gray"
    if score < 0.4:
        return "red"
    elif score < 0.7:
        return "orange"
    else:
        return "green"


# =========================================================
# Timeline Plot Generation
# =========================================================

def main():

    db_path = "output/fused_timeline.db"

    if not os.path.exists(db_path):
        print("❌ Database not found. Run pipeline first.")
        return

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("""
        SELECT device_id, corrected_timestamp, confidence_score
        FROM timeline
        WHERE corrected_timestamp IS NOT NULL
        ORDER BY corrected_timestamp
    """)

    rows = cur.fetchall()
    conn.close()

    if not rows:
        print("⚠ No timeline data found.")
        return

    devices = sorted(set(r[0] for r in rows))
    device_index = {device: i for i, device in enumerate(devices)}

    plt.figure(figsize=(10, 4))

    for device_id, timestamp, confidence in rows:
        try:
            dt = datetime.fromisoformat(timestamp)
        except ValueError:
            continue

        y = device_index[device_id]
        color = classify_color(confidence)

        plt.scatter(dt, y, color=color, s=30)

    # Axis formatting
    plt.yticks(range(len(devices)), devices)
    plt.xlabel("Time")
    plt.ylabel("Device")
    plt.title("Timeline View (Confidence Coloured)")
    plt.grid(True)

    # Legend (manual for clarity)
    plt.scatter([], [], color="green", label="High Confidence")
    plt.scatter([], [], color="orange", label="Medium Confidence")
    plt.scatter([], [], color="red", label="Low Confidence")
    plt.legend(loc="upper right")

    os.makedirs("output", exist_ok=True)
    plt.tight_layout()
    plt.savefig("output/timeline_visualisation.png", dpi=300)
    plt.close()

    print("✔ Timeline visualisation saved to: output/timeline_visualisation.png")


if __name__ == "__main__":
    main()
