import os
from core.drive_sense import get_drive_type

class SmartScanner:
    def __init__(self, job_mgr):
        self.jm = job_mgr
        self.small_buffer = []
        self.small_size = 0
        self.current_dest_root = ""
        self.buffer_limit = 50 * 1024 * 1024 # 50MB per batch

    def process_path(self, src, dest, config):
        self.current_dest_root = dest
        # Detect drive type for this source
        drive_type = get_drive_type(src)
        self.jm.source_types[src] = drive_type
        
        self._scan_recursive(src, src)
        self.flush_small()

    def _scan_recursive(self, root, current_path):
        try:
            with os.scandir(current_path) as it:
                for entry in it:
                    if entry.is_dir():
                        self._scan_recursive(root, entry.path)
                    else:
                        file_obj = {
                            "src": entry.path,
                            "rel": os.path.relpath(entry.path, root),
                            "size": entry.stat().st_size
                        }
                        self.add_to_small_buffer(file_obj)
        except PermissionError: pass

    def add_to_small_buffer(self, file_obj):
        self.small_buffer.append(file_obj)
        self.small_size += file_obj["size"]
        if self.small_size >= self.buffer_limit or len(self.small_buffer) >= 100:
            self.flush_small()

    def flush_small(self):
        if not self.small_buffer: return
        self.jm.add_batch(self.small_buffer, self.small_size, self.current_dest_root)
        self.small_buffer = []
        self.small_size = 0