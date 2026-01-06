import os
import importlib
import inspect
from core.interfaces import IDataSource, IDataDest, ITransferStrategy, ITool, ISystemSetting

class PluginManager:
    def __init__(self):
        self.sources = []
        self.dests = []
        self.strategies = []
        self.tools = []
        self.settings = []

    def load_all(self):
        p_dir = "plugins"
        if not os.path.exists(p_dir): return
        
        # Clear lists
        self.sources = []; self.dests = []; self.strategies = []; self.tools = []; self.settings = []
        
        for f in os.listdir(p_dir):
            if f.endswith(".py") and not f.startswith("__"):
                mod_name = f"plugins.{f[:-3]}"
                try:
                    mod = importlib.import_module(mod_name)
                    for name, obj in inspect.getmembers(mod):
                        if inspect.isclass(obj) and obj.__module__ == mod_name:
                            # CRITICAL FIX: Check Type BEFORE Instantiating
                            # This prevents the loader from trying to launch UI Windows (like DeleteWindow)
                            
                            if issubclass(obj, IDataSource) and obj is not IDataSource:
                                self.sources.append(obj())
                                
                            elif issubclass(obj, IDataDest) and obj is not IDataDest:
                                self.dests.append(obj())
                                
                            elif issubclass(obj, ITransferStrategy) and obj is not ITransferStrategy:
                                self.strategies.append(obj())
                                
                            elif issubclass(obj, ITool) and obj is not ITool:
                                self.tools.append(obj())
                                
                            elif issubclass(obj, ISystemSetting) and obj is not ISystemSetting:
                                self.settings.append(obj())
                            
                except Exception as e:
                    print(f"Error loading {f}: {e}")