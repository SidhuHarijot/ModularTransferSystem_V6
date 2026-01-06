
import threading
import time

class TelemetryHub:
    """
    Hot metrics live in RAM.
    Slow snapshot is produced by SnapshotFlusher.
    """
    def __init__(self):
        self._lock = threading.Lock()
        self.state = {
            "run_status": "IDLE",
            "total_bytes": 0,
            "done_bytes": 0,
            "total_files": 0,
            "done_files": 0,
            "speed_mb_s": 0.0,
            "files_s": 0.0,
            "active_threads": 0,
            "batches_done": 0,
            "batches_total": 0,
            "pct": 0.0,
            "eta_sec": None,
            "ts": time.time(),
        }
        # Optional: per-stream hot metrics (not flushed every time)
        self.streams = {}  # stream_id -> dict

    def update(self, **kwargs):
        with self._lock:
            self.state.update(kwargs)
            self.state["ts"] = time.time()

    def snapshot(self):
        with self._lock:
            return dict(self.state)

    def update_stream(self, stream_id, **kwargs):
        with self._lock:
            s = self.streams.get(stream_id) or {}
            s.update(kwargs)
            self.streams[stream_id] = s

    def snapshot_streams(self, max_items=16):
        with self._lock:
            items = []
            for k, v in list(self.streams.items())[:max_items]:
                items.append({"id": k, **v})
            return items
