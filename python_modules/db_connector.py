import sqlite3
from datetime import datetime

class DB:
    def __init__(self, db_path="events.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.setup_tables()

    def setup_tables(self):
        # Create events table
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            event_type TEXT,
            details TEXT
        )
        """)
        # Optional: whitelist table
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS whitelist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE
        )
        """)
        self.conn.commit()

    def insert_event(self, event_type, details):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute(
            "INSERT INTO events (timestamp, event_type, details) VALUES (?, ?, ?)",
            (timestamp, event_type, details)
        )
        self.conn.commit()

    def fetch_events(self):
        self.cursor.execute("SELECT * FROM events ORDER BY timestamp DESC")
        return self.cursor.fetchall()

    def add_to_whitelist(self, name):
        try:
            self.cursor.execute("INSERT OR IGNORE INTO whitelist (name) VALUES (?)", (name,))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Whitelist error: {e}")

    def get_whitelist(self):
        self.cursor.execute("SELECT name FROM whitelist")
        return [row[0] for row in self.cursor.fetchall()]

    def fetch_recent(self, n=100):
        self.cursor.execute("SELECT * FROM events ORDER BY timestamp DESC LIMIT ?", (n,))
        return self.cursor.fetchall()

