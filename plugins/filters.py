import os
from core.interfaces import IFilter

class ConfigurableFilter(IFilter):
    def __init__(self, config=None):
        self.config = config or {}
        self.junk_substrings = []
        
        # 1. Base Junk (Always bad)
        self.junk_substrings.extend(["$recycle.bin", "system volume information", "pagefile.sys", "hiberfil.sys"])
        
        # 2. Configurable Junk
        if self.config.get('skip_temp', False):
            self.junk_substrings.extend(["\\appdata\\local\\temp", "\\windows\\temp", "\\cache"])
            
        if self.config.get('skip_appdata', False):
            self.junk_substrings.append("\\appdata\\")
            
        if self.config.get('skip_windows', False):
            self.junk_substrings.append("\\windows\\")

    def should_skip(self, path):
        path_lower = path.lower()
        for junk in self.junk_substrings:
            if junk in path_lower:
                return True
        return False