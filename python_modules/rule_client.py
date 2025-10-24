import socket
import os

SOCKET_PATH = '/tmp/guardian_rules.sock'

class RuleClient:
    def __init__(self, socket_path=SOCKET_PATH, timeout=2):
        self.socket_path = socket_path
        self.timeout = timeout

    def evaluate(self, event_type, details):
        if not os.path.exists(self.socket_path):
            raise FileNotFoundError(f"Rule engine socket not found at {self.socket_path}")
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
            s.settimeout(self.timeout)
            s.connect(self.socket_path)
            payload = f"{event_type}|{details}"
            s.sendall(payload.encode('utf-8'))
            resp = s.recv(16).decode('utf-8').strip()
            try:
                return int(resp)
            except Exception:
                return 0

# module-level convenience
_client = RuleClient()

def evaluate_event(event_type, details):
    return _client.evaluate(event_type, details)
