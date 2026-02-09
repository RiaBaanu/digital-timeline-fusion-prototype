from pipeline.timeline_queries import (
    get_all_events,
    get_events_by_device,
    get_events_in_time_range
)

db_path = "db/fused_timeline.db"

print("=== ALL EVENTS ===")
events = get_all_events(db_path)
for e in events:
    print(e[1], e[3], e[4])  # device_id, corrected_timestamp, event_type

print("\n=== PHONE01 EVENTS ===")
phone_events = get_events_by_device(db_path, "Phone01")
for e in phone_events:
    print(e[1], e[3], e[4])

print("\n=== EVENTS BETWEEN 13:11 and 13:12 ===")
range_events = get_events_in_time_range(
    db_path,
    "2024-04-23T13:11:00+00:00",
    "2024-04-23T13:12:00+00:00"
)
for e in range_events:
    print(e[1], e[3], e[4])
