import json
import os
import datetime

class AuditLogger:
    def __init__(self, filepath="audit_log.json"):
        self.filepath = filepath
        self.log_data = []
        # Clear previous log
        if os.path.exists(self.filepath):
            os.remove(self.filepath)
            
    def log(self, module, event_type, data):
        entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "module": module,
            "event_type": event_type,
            "data": data
        }
        self.log_data.append(entry)
        
        # Save to disk iteratively
        with open(self.filepath, "w") as f:
            json.dump(self.log_data, f, indent=2)
