import os
from core.interfaces import IVerifier

class QuickVerifier(IVerifier):
    def verify(self, src, dst):
        try:
            s = os.stat(src)
            d = os.stat(dst)
            # Match if size is same AND modification time is close (within 2s)
            return s.st_size == d.st_size and abs(s.st_mtime - d.st_mtime) < 2
        except: return False