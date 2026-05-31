import json
import time
import os

def replay_audit_log(filepath="audit_log.json"):
    if not os.path.exists(filepath):
        print(f"Error: {filepath} not found.")
        return

    with open(filepath, "r") as f:
        log_data = json.load(f)

    print("=====================================================")
    print("  QUANTUM_JEDI AUDIT REPLAY (JSON INGESTION)         ")
    print("=====================================================\n")

    for entry in log_data:
        timestamp = entry["timestamp"]
        module = entry["module"]
        event = entry["event_type"]
        data = entry["data"]

        print(f"[{module}] {event}")
        for k, v in data.items():
            print(f"   -> {k}: {v}")
        print("-" * 40)
        time.sleep(0.5)

    print("\n=====================================================")
    print("  END OF REPLAY. SYSTEM SURVIVED STRESS DEMO.        ")
    print("=====================================================")

if __name__ == "__main__":
    replay_audit_log()
