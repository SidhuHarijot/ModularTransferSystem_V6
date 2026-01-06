import json
import os

class StateManager:
    def __init__(self):
        self.state_file = "system_restore_state.json"
        self.data = {}
        self.load()

    def load(self):
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    self.data = json.load(f)
            except: self.data = {}

    def save_original(self, key, value):
        # Only save if we haven't already saved it (don't overwrite original with modified)
        if key not in self.data:
            self.data[key] = value
            with open(self.state_file, 'w') as f:
                json.dump(self.data, f, indent=2)

    def get_original(self, key):
        return self.data.get(key)

    def clear_key(self, key):
        if key in self.data:
            del self.data[key]
            with open(self.state_file, 'w') as f:
                json.dump(self.data, f, indent=2)