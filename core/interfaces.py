from abc import ABC, abstractmethod

class IDataSource(ABC):
    @property
    @abstractmethod
    def display_name(self): pass
    @abstractmethod
    def scan_to_manifest(self, path, job_mgr, config=None): pass

class IDataDest(ABC):
    @property
    @abstractmethod
    def display_name(self): pass
    @abstractmethod
    def ensure_dir(self, path): pass
    @abstractmethod
    def exists(self, path): pass

class ITransferStrategy(ABC):
    @property
    @abstractmethod
    def name(self): pass
    @abstractmethod
    def execute_job(self, job_mgr, src, dst, callback, config=None): pass

class ITool(ABC):
    @property
    @abstractmethod
    def name(self): pass
    @abstractmethod
    def run(self, parent): pass

class IFilter(ABC):
    @abstractmethod
    def should_skip(self, path): pass

class IVerifier(ABC):
    @abstractmethod
    def verify(self, src, dst): pass

class ILogger(ABC):
    @abstractmethod
    def log_batch(self, batch_id, count, size, duration): pass
    @abstractmethod
    def save_session(self): pass

# --- V14 UPDATE: STATE AWARE SETTINGS ---
class ISystemSetting(ABC):
    @property
    @abstractmethod
    def name(self): pass
    
    @property
    @abstractmethod
    def description(self): pass
    
    @abstractmethod
    def check_state(self):
        """Returns True if optimization is currently ACTIVE"""
        pass

    @abstractmethod
    def apply(self, state_mgr): 
        """Apply optimization and save original state"""
        pass
        
    @abstractmethod
    def revert(self, state_mgr): 
        """Revert to original state"""
        pass