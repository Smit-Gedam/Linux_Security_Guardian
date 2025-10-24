#!/bin/bash
set -e
# Install python deps
python3 -m pip install --user -r requirements.txt
# Create virtual folders
mkdir -p db logs
# Create sqlite DB if not exists
python3 - <<'PY'
import sqlite3
conn = sqlite3.connect('db/events.db')
c = conn.cursor()
# Create tables
c.execute('''CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    event_type TEXT,
    details TEXT,
    severity INTEGER
)''')
c.execute('''CREATE TABLE IF NOT EXISTS whitelist (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    path TEXT
)''')
conn.commit()
conn.close()
PY
# Build C rule engine
cd c_modules
make || gcc rules_engine_socket.c -o rules_engine_socket
cd ..

echo "Setup complete. Start rule engine server: ./c_modules/rules_engine_socket &"
