import time
import os
import csv
import json
from core.html_reporter import HtmlLiveReporter

class TelemetryHandler:
    def __init__(self, job_mgr, plugin_mgr, stream_var):
        self.jm = job_mgr
        self.pm = plugin_mgr
        self.stream_var = stream_var
        self.live_html = HtmlLiveReporter()
        self.csv_path = os.path.join(os.path.expanduser("~"), "Desktop", "Transfer_Log.csv")
        
        self.last_update_time = 0
        self.last_files_count = 0
        self.last_batches_count = 0
        self.last_bytes_count = 0
        
        self.cached_speed = 0
        self.cached_fps = 0
        self.cached_bps = 0
        self.graph_history = [0] * 20
        
        self.static_data = {
            "total_files": 0, "total_bytes": 1, "total_batches": 0,
            "big_batches": 0, "small_batches": 0, "total_folders": 0
        }
        
        self.master_state = {
            "stream_avg_speed": 0, "stream_avg_fps": 0, "stream_avg_bps": 0, "streams": 8,
            "avg_speed": 0, "avg_files_sec": 0, "avg_batches_sec": 0, "active_time": 0,
            "pct_data": 0, "done_bytes": 0, "done_files": 0, "done_batches": 0,
            **self.static_data,
            "sys_state": {}, "run_status": "IDLE", "history": {}, "speed_history": []
        }
        
        self.update_log("STATE")

    def refresh_static_data(self):
        all_batches = self.jm.job_data.get("batches", [])
        big_count = sum(1 for b in all_batches if b["total_size"] > 400*1024*1024)
        total_b = sum(b["total_size"] for b in all_batches)
        
        self.static_data = {
            "total_files": self.jm.job_data.get("total_files", 0),
            "total_bytes": total_b if total_b > 0 else 1,
            "total_batches": len(all_batches),
            "big_batches": big_count,
            "small_batches": len(all_batches) - big_count,
            "total_folders": self.jm.job_data.get("total_folders", 0)
        }
        self.master_state.update(self.static_data)
        self.live_html.update_from_state(self.master_state)

    def update_log(self, log_type, **kwargs):
        now = time.time()
        
        if log_type == "PERIODIC":
            if (now - self.last_update_time) < 1.0: return
            bytes_session = kwargs.get('bytes_session', 0)
            delta_t = now - self.last_update_time
            
            if delta_t > 0:
                d_bytes = bytes_session - self.last_bytes_count
                self.cached_speed = (d_bytes / 1048576) / delta_t
                self.graph_history.append(self.cached_speed)
                if len(self.graph_history) > 20: self.graph_history.pop(0)
                self.last_bytes_count = bytes_session
                self.last_update_time = now
            
            active_dur = self.jm.get_active_time()
            done_bytes = self.jm.get_total_bytes_done()
            pct = (done_bytes / self.static_data['total_bytes'] * 100) if self.static_data['total_bytes'] > 0 else 0
            
            self.master_state.update({
                "pct_data": pct,
                "done_bytes": done_bytes,
                "done_files": self.jm.session_files_done,
                "active_time": active_dur,
                "speed_history": self.graph_history
            })

        elif log_type == "STATE":
            run_status = kwargs.get('run_status', self.master_state['run_status'])
            sys_state = {}
            
            # V58.1 FIX: Added None check for Plugin Manager
            if self.pm and hasattr(self.pm, 'settings'):
                for s in self.pm.settings:
                    sys_state[s.name] = s.check_state()
            
            self.master_state.update({
                "sys_state": sys_state,
                "run_status": run_status
            })

        self.live_html.update_from_state(self.master_state)