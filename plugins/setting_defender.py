import subprocess
import os
from core.interfaces import ISystemSetting

class DefenderSetting(ISystemSetting):
    @property
    def name(self): return "Defender Exclusions"
    @property
    def description(self): return "Whitelists C:/D: drives"

    def check_state(self):
        # Check if C:\ is in exclusion list
        try:
            # We use 4 backslashes here so python writes 2 to the file, which means 1 literal backslash in string
            res = subprocess.check_output("powershell Get-MpPreference", shell=True).decode()
            return "ExclusionPath" in res and "C:\\" in res
        except: return False

    def apply(self, state_mgr):
        # Fix escaping for the string "C:" and "D:"
        cmd = "Add-MpPreference -ExclusionPath 'C:\\', 'D:\\'"
        try:
            subprocess.run(["powershell", "-Command", cmd], shell=True, check=True)
            return True, "Exclusions Added"
        except: return False, "Run as Admin!"

    def revert(self, state_mgr):
        cmd = "Remove-MpPreference -ExclusionPath 'C:\\', 'D:\\'"
        try:
            subprocess.run(["powershell", "-Command", cmd], shell=True, check=True)
            return True, "Exclusions Removed"
        except: return False, "Run as Admin!"