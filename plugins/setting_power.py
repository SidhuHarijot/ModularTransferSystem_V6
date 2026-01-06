import subprocess
from core.interfaces import ISystemSetting

class PowerSetting(ISystemSetting):
    @property
    def name(self): return "Prevent Sleep"
    @property
    def description(self): return "Sets Screen Timeout to 'Never'"

    def _get_current(self):
        # Returns current timeout in minutes (string)
        try:
            res = subprocess.check_output("powercfg /q", shell=True).decode()
            # Parsing powercfg is hard, so we assume check is based on applying.
            # Real implementation requires regex on GUIDs. 
            # For this demo, we assume False unless tracked.
            return "15" 
        except: return "15"

    def check_state(self):
        # In a real app, query powercfg. Here we simplify.
        return False 

    def apply(self, state_mgr):
        # 1. Save Original (Mock: assume 15 min default if can't read)
        state_mgr.save_original("monitor_timeout", "15") 
        
        # 2. Apply 0 (Never)
        cmd = "powercfg /change monitor-timeout-ac 0"
        try:
            subprocess.run(cmd, shell=True, check=True)
            return True, "Sleep Disabled (0 min)"
        except: return False, "Failed"

    def revert(self, state_mgr):
        # 1. Get Original
        orig = state_mgr.get_original("monitor_timeout") or "15"
        
        cmd = f"powercfg /change monitor-timeout-ac {orig}"
        try:
            subprocess.run(cmd, shell=True, check=True)
            state_mgr.clear_key("monitor_timeout")
            return True, f"Restored Timeout to {orig} min"
        except: return False, "Failed"