
import json
import time
from pathlib import Path

class SnapshotFlusher:
    """
    Writes a tiny JSON snapshot occasionally to avoid disk thrash.
    Atomic write: temp -> replace.
    """
    def __init__(self, hub, out_path: Path, interval_sec=15):
        self.hub = hub
        self.out_path = Path(out_path)
        self.interval_sec = max(5, int(interval_sec))
        self._stop = False
        self._last_written = None

    def stop(self):
        self._stop = True

    def _should_write(self, snap):
        # Write only if something changed meaningfully, or time elapsed
        key = (snap.get("run_status"), int(snap.get("done_bytes", 0) // (50 * 1024 * 1024)), int(time.time() // self.interval_sec))
        return key != self._last_written

    def run_forever(self):
        while not self._stop:
            try:
                snap = self.hub.snapshot()
                # Optionally include a SMALL subset of streams for dashboard dots
                snap["streams"] = self.hub.snapshot_streams(max_items=12)

                if self._should_write(snap):
                    self.out_path.parent.mkdir(parents=True, exist_ok=True)
                    tmp = self.out_path.with_suffix(".tmp")
                    tmp.write_text(json.dumps(snap), encoding="utf-8")
                    tmp.replace(self.out_path)
                    self._last_written = (snap.get("run_status"), int(snap.get("done_bytes", 0) // (50 * 1024 * 1024)), int(time.time() // self.interval_sec))
            except Exception:
                pass

            time.sleep(1)
