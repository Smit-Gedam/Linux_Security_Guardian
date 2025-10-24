import subprocess
from .db_connector import DB
from .utils import timestamp
from .rule_client import evaluate_event
import time

DBI = DB()
BLACKLISTED_PREFIXES = ['198.51.100.', '203.0.113.']

def parse_netstat():
    try:
        out = subprocess.check_output(['ss','-tunp'], text=True)
    except Exception:
        out = subprocess.check_output(['netstat','-tunp'], text=True)
    lines = out.splitlines()
    for line in lines:
        for prefix in BLACKLISTED_PREFIXES:
            if prefix in line:
                severity = evaluate_event('NETWORK', line)
                if severity > 0:
                    DBI.insert_event(timestamp(), 'NETWORK', line.strip(), severity)

if __name__ == '__main__':
    while True:
        parse_netstat()
        time.sleep(10)
