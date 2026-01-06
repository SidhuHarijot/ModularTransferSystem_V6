import time
import json
import os
from core.interfaces import ILogger

class SessionLogger(ILogger):
    def __init__(self):
        self.data = {"start": time.ctime(), "batches": []}
        
    def log_batch(self, batch_id, count, size, duration):
        pass 
        
    def save_session(self):
        pass