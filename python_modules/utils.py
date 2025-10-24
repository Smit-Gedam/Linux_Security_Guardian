import os
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(ROOT, 'db', 'events.db')
RULES_SOCKET = '/tmp/guardian_rules.sock'

def timestamp():
    return datetime.utcnow().isoformat() + 'Z'
