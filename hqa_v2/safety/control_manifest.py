import json
import hashlib
import datetime

class ControlManifest:
    """
    Packages hardware-facing commands into a cryptographically 
    verifiable JSON manifest with explicit dry-run flags.
    """
    @staticmethod
    def create_manifest(issuer_module, target_system, command_intent, dry_run=True):
        payload = {
            "timestamp": datetime.datetime.now().isoformat(),
            "issuer": issuer_module,
            "target": target_system,
            "intent": command_intent,
            "dry_run": dry_run
        }
        
        # Simple SHA256 to ensure integrity
        manifest_string = json.dumps(payload, sort_keys=True)
        signature = hashlib.sha256(manifest_string.encode('utf-8')).hexdigest()
        
        return {
            "payload": payload,
            "signature": signature
        }
