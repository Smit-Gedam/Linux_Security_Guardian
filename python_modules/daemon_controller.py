# unchanged threading structure but modules now use rule_client
# ensure rule engine server is running before starting daemon

import threading
import time
from .monitor_process import scan_processes
from .monitor_files import monitor_path
from .monitor_network import parse_netstat

if __name__ == '__main__':
    t1 = threading.Thread(target=lambda: [scan_processes() or time.sleep(5) for _ in iter(int,1)], daemon=True)
    t2 = threading.Thread(target=lambda: [parse_netstat() or time.sleep(10) for _ in iter(int,1)], daemon=True)
    t3 = threading.Thread(target=lambda: monitor_path('/etc'), daemon=True)
    t1.start(); t2.start(); t3.start()
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        print('Shutting down')
