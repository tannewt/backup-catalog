import json
import pathlib
import os
import sys

root = pathlib.Path(sys.argv[1])

for fn in root.glob("**/event_sessions.json"):
    events = json.loads(fn.read_text())
    for event in events:
        thumb = fn.parent / (event["session_id"] + ".jpeg")
        if not thumb.exists():
            continue
        ts = event["start_time"]["seconds"] * 1000000000 + event["start_time"].get("nanos", 0)
        os.utime(thumb, ns=(ts, ts))
