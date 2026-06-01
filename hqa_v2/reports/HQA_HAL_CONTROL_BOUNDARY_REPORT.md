# HQA HAL Control Boundary Report (Phase 3)

This report demonstrates that the HALSafetyGovernor scans Control Manifests and enforces the boundary between software intelligence and physical execution in this proxy test.

## Test Cases Executed:
1. **Dry-Run Enforcement**: Command packaged as a manifest, simulating physical SCPI acknowledgments without touching hardware.
2. **Thermal Violation**: Attempted to dispatch cooling intensity (20.0) higher than the policy limit (15.0). Blocked.
3. **Forbidden Action**: Attempted to dispatch banned command `EMERGENCY_VENT`. Blocked.

## JSON Audit Log
```json
[
  {
    "timestamp": "2026-05-31T22:09:31.277190",
    "module": "SYSTEM",
    "event_type": "HAL_SAFETY_DEMO_START",
    "data": {
      "version": "Phase-3"
    }
  },
  {
    "timestamp": "2026-05-31T22:09:31.277694",
    "module": "SAFETY_GOVERNOR",
    "event_type": "MANIFEST_RECEIVED",
    "data": {
      "issuer": "HAL_BRIDGE",
      "dry_run": true
    }
  },
  {
    "timestamp": "2026-05-31T22:09:31.277694",
    "module": "SAFETY_GOVERNOR",
    "event_type": "DRY_RUN_ENFORCED",
    "data": {
      "action": "Simulating SCPI Acknowledgement. No hardware touched."
    }
  },
  {
    "timestamp": "2026-05-31T22:09:31.278219",
    "module": "SAFETY_GOVERNOR",
    "event_type": "MANIFEST_RECEIVED",
    "data": {
      "issuer": "HAL_BRIDGE",
      "dry_run": false
    }
  },
  {
    "timestamp": "2026-05-31T22:09:31.278219",
    "module": "SAFETY_GOVERNOR",
    "event_type": "MANIFEST_REJECTED",
    "data": {
      "reason": "THERMAL_VIOLATION: Intensity 20.0 > 15.0"
    }
  },
  {
    "timestamp": "2026-05-31T22:09:31.278219",
    "module": "HAL_BRIDGE",
    "event_type": "EXECUTION_ABORTED",
    "data": {
      "reason": "governor_lockdown"
    }
  },
  {
    "timestamp": "2026-05-31T22:09:31.278731",
    "module": "SAFETY_GOVERNOR",
    "event_type": "MANIFEST_RECEIVED",
    "data": {
      "issuer": "HAL_BRIDGE",
      "dry_run": false
    }
  },
  {
    "timestamp": "2026-05-31T22:09:31.278731",
    "module": "SAFETY_GOVERNOR",
    "event_type": "MANIFEST_REJECTED",
    "data": {
      "reason": "FORBIDDEN_ACTION: EMERGENCY_VENT"
    }
  },
  {
    "timestamp": "2026-05-31T22:09:31.278731",
    "module": "HAL_BRIDGE",
    "event_type": "EXECUTION_ABORTED",
    "data": {
      "reason": "governor_lockdown"
    }
  },
  {
    "timestamp": "2026-05-31T22:09:31.278731",
    "module": "SYSTEM",
    "event_type": "HAL_SAFETY_DEMO_COMPLETE",
    "data": {
      "status": "boundaries_held"
    }
  }
]
```
