import csv
import time
import os

class BlackBoxLogger:
    def __init__(self):
        self.log_path = os.path.join(os.path.expanduser("~"), "Desktop", "GeekSquad_Operation_Log.csv")
        self.active = False
        self.job_mgr = None

    def start(self, job_mgr):
        self.active = True
        self.job_mgr = job_mgr
        
        # V53.1 FIX: Handle Multi-Source Lists
        # Old code used job_mgr.job_data['src'] which caused KeyError
        
        sources = job_mgr.job_data.get("sources", [])
        if isinstance(sources, list):
            src_str = ", ".join(sources)
        else:
            src_str = str(sources)
            
        dests = job_mgr.job_data.get("destinations", [])
        if isinstance(dests, list):
            dst_str = ", ".join(dests)
        else:
            dst_str = str(dests)

        self.log("SYSTEM", "JOB STARTED", f"Sources: [{src_str}] -> Dests: [{dst_str}]")

    def stop(self):
        if self.active:
            self.log("SYSTEM", "JOB STOPPED", "User initiated stop or job complete.")
            self.active = False

    def log(self, category, event, details):
        # Writes a structured log entry
        if not self.active: return
        
        try:
            file_exists = os.path.exists(self.log_path)
            with open(self.log_path, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow(["TIMESTAMP", "CATEGORY", "EVENT", "DETAILS"])
                
                writer.writerow([
                    time.strftime("%Y-%m-%d %H:%M:%S"),
                    category.upper(),
                    event.upper(),
                    details
                ])
        except: pass