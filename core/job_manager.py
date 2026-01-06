import threading
import time

class JobManager:
    def __init__(self):
        self.job_data = {
            "sources": [],
            "destinations": [],
            "batches": [], 
            "total_files": 0, 
            "total_size": 0, 
            "status": "Idle"
        }

        self.history = {}
        self.session_files_done = 0
        self.bytes_done = 0
        self.last_bytes = 0
        self.last_time = time.time()
        self.cancel_flag = False
        self.pause_event = threading.Event()
        self.pause_event.set()
        
        # Drive metadata
        self.source_types = {}

    def reset_flags(self):
        self.cancel_flag = False
        self.bytes_done = 0
        self.session_files_done = 0
        self.job_data["status"] = "Running"
        self.pause_event.set()

    def start_clock(self):
        self.last_time = time.time()
        self.last_bytes = 0

    def create_new_job(self, sources, destinations):
        self.job_data = {
            "sources": sources, 
            "destinations": destinations, 
            "batches": [], 
            "total_files": 0, 
            "total_size": 0, 
            "status": "Idle"
        }
        self.source_types = {}

    def get_destination_for_source(self, idx):
        dest_list = self.job_data.get("destinations", [])
        if idx < len(dest_list):
            return dest_list[idx]
        return dest_list[0] if dest_list else None

    # FIXED: Added the missing batch handler for the scanner
    def add_batch(self, files_list, total_size, dest_root):
        batch_id = f"B-{len(self.job_data['batches']) + 1}"
        batch = {
            "id": batch_id,
            "dest_root": dest_root,
            "files": list(files_list),
            "total_size": total_size,
            "status": "pending"
        }
        self.job_data["batches"].append(batch)
        self.job_data["total_files"] += len(files_list)
        self.job_data["total_size"] += total_size

    def get_current_speed_mb(self):
        now = time.time()
        diff = now - self.last_time
        if diff < 0.5: return 0
        speed = ((self.bytes_done - self.last_bytes) / 1048576) / diff
        return max(0, speed)
    
    def get_pending_batches(self):
        """
        Returns a list of all batches that are still pending.
        """
        return [b for b in self.job_data.get("batches", []) if b.get("status") == "pending"]

    def mark_batch_done(self, batch_id):
        for b in self.job_data.get("batches", []):
            if b.get("id") == batch_id:
                b["status"] = "done"
                try:
                    self.session_batches_done += 1
                except Exception:
                    pass
                return
