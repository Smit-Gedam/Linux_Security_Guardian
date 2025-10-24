import psutil
from .db_connector import DB
from .utils import timestamp
from .rule_client import evaluate_event

DBI = DB()

def scan_processes():
    for proc in psutil.process_iter(['pid','name','exe','username']):
        try:
            info = proc.info
            path = info.get('exe') or info.get('name') or ''
            severity = evaluate_event('PROCESS', path)
            if severity > 0:
                DBI.insert_event(timestamp(), 'PROCESS', f"{path} (pid={info.get('pid')})", severity)
        except (psutil.NoSuchProcess, FileNotFoundError):
            continue

if __name__ == '__main__':
    scan_processes()
