import time
from core.transfer_config import TransferConfig

class AutoTuner:
    def __init__(self, job_mgr):
        self.jm = job_mgr
        self.cfg = TransferConfig()
        
        self.enabled = self.cfg.get("auto_tune_enabled")
        self.min_threads = self.cfg.get("min_threads")
        self.max_threads = self.cfg.get("max_threads")
        self.current_target = self.cfg.get("starting_threads")
        
        # State
        self.last_check = 0
        self.last_speed = 0
        self.trend = 0 # -1: Dropping, 0: Stable, 1: Climbing
        self.status_msg = "STABLE"

    def get_target_threads(self, current_speed_mb):
        if not self.enabled: 
            return self.current_target
            
        now = time.time()
        if now - self.last_check < 5.0: # Check every 5 seconds
            return self.current_target
            
        # TUNE LOGIC
        delta = current_speed_mb - self.last_speed
        
        # If speed increased by > 5MB/s, we are on the right track
        if delta > 5.0:
            if self.current_target < self.max_threads:
                self.current_target += 2
                self.status_msg = "BOOSTING (+)"
        
        # If speed dropped significantly, we are choking IO
        elif delta < -10.0:
             if self.current_target > self.min_threads:
                 self.current_target -= 2
                 self.status_msg = "THROTTLING (-)"
        
        # If flat, try creeping up slowly to find limit
        else:
             if self.current_target < self.max_threads:
                 self.current_target += 1
                 self.status_msg = "SEEKING (>)"

        # CLAMP
        self.current_target = max(self.min_threads, min(self.max_threads, self.current_target))
        
        self.last_check = now
        self.last_speed = current_speed_mb
        return self.current_target