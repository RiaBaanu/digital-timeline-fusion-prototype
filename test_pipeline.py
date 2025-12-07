import datetime
from dateutil import parser

# --- Sample raw artefacts ---

raw_events = [
    {
        "device": "Phone",
        "timestamp": "2024-04-23 13:17:40",   # local time
        "event_type": "App Launch",
        "provenance": ("phone_sms.db", 142)
    },
    {
        "device": "Laptop",
        "timestamp": "2024-04-23T13:14:32Z",  # already UTC
        "event_type": "Email Sent",
        "provenance": ("mail.json", 55)
    },
    {
        "device": "Camera",
        "timestamp": "2024-04-23 08:10:15",   # device running 5 mins slow
        "event_type": "Motion Detected",
        "provenance": ("iot_cam.csv", 88)
    }
]

# --- Timestamp Normalisation ---
def normalise(ts):
    return parser.parse(ts).astimezone(datetime.timezone.utc)

normalised_events = []
for e in raw_events:
    e["original_utc"] = normalise(e["timestamp"])
    normalised_events.append(e)

# --- Skew Correction (very simple example) ---
# Let's assume we know Camera is -5 minutes compared to Phone
device_offsets = {
    "Camera": datetime.timedelta(minutes=5),
    "Phone": datetime.timedelta(minutes=0),
    "Laptop": datetime.timedelta(minutes=0)
}

for e in normalised_events:
    e["corrected"] = e["original_utc"] + device_offsets[e["device"]]

# --- Fusion (simple chronological ordering) ---
fused = sorted(normalised_events, key=lambda x: x["corrected"])

# --- Print fused timeline ---
print("FUSED TIMELINE:")
for e in fused:
    print(
        f"{e['corrected']} | {e['event_type']} | {e['device']} | "
        f"Provenance: {e['provenance']}"
    )
