from core.state_manager import StateManager

class SystemConfigManager:
    def __init__(self, plugin_mgr):
        self.pm = plugin_mgr
        self.sm = StateManager() # Persist state
        
    def run_prep(self, enabled_names=None):
        results = []
        for setting in self.pm.settings:
            if enabled_names is None or setting.name in enabled_names:
                # Check if already active
                if setting.check_state():
                    results.append(f"[SKIP] {setting.name}: Already Active")
                    continue
                    
                success, msg = setting.apply(self.sm)
                status = "✔" if success else "❌"
                results.append(f"[{status}] {setting.name}: {msg}")
        return results

    def run_cleanup(self):
        results = []
        for setting in self.pm.settings:
            # We assume revert handles the logic of "is it needed?"
            success, msg = setting.revert(self.sm)
            results.append(f"[REVERT] {setting.name}: {msg}")
        return results