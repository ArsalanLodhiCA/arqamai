# store.py

import json
from datetime import datetime

def save_events_to_file(events: list[dict], filename: str = None):
    if not filename:
        filename = f"events_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(events, f, indent=2, ensure_ascii=False)

    print(f"✅ Saved {len(events)} events to {filename}")
