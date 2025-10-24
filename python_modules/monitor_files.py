from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from .db_connector import DB
from .utils import timestamp
from .rule_client import evaluate_event
import time

DBI = DB()

class MonitorHandler(FileSystemEventHandler):
    def on_modified(self, event):
        path = event.src_path
        severity = evaluate_event('FILE_MOD', path)
        if severity > 0:
            DBI.insert_event(timestamp(), 'FILE_MOD', path, severity)

def monitor_path(path):
    event_handler = MonitorHandler()
    observer = Observer()
    observer.schedule(event_handler, path=path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == '__main__':
    monitor_path('/etc')
