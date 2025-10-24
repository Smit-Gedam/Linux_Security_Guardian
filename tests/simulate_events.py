import time
import random
import os
from python_modules.db_connector import DB

# Ensure db directory exists
os.makedirs("db", exist_ok=True)

# Use consistent database path
db = DB("db/events.db")

# Sample event types and details
EVENT_TYPES = [
    "PROCESS_ALERT",
    "NETWORK_WARNING",
    "LOGIN_ATTEMPT",
    "FILE_CHANGE",
    "SERVICE_RESTART"
]

DETAILS = [
    "Detected suspicious process 'nc'",
    "Unusual outbound connection to 192.168.1.100:4444",
    "Failed SSH login from 203.0.113.45",
    "Critical system file /etc/passwd modified",
    "System service sshd restarted unexpectedly"
]

def simulate_events(num_events=10, delay=0.2):
    for i in range(num_events):
        event_type = random.choice(EVENT_TYPES)
        detail = random.choice(DETAILS)
        db.insert_event(event_type, detail)
        print(f"[+] Inserted event {i+1}: {event_type} - {detail}")
        time.sleep(delay)

if __name__ == "__main__":
    simulate_events(15)
    print("\n✅ Simulation complete. Check db/events.db for inserted records.")

