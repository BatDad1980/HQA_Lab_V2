# Alice & Bob: Cat-Qubit HQA Integration Report (Fail-Closed Demonstration)

A cat-qubit-style fabric demonstration. Bit-flip (X) suppression is treated as a modeled hardware assumption; phase-flip (Z) exposure is the live threat. Two phase-flip faults are injected, detected, and quarantined, then a corner-to-corner route is requested. This report records whatever actually happened.

## Setup
- Injected phase-flip faults: Q_1_1, Q_3_3.
- Route requested: `Q_0_0` -> `Q_4_4`.

## Outcome
No safe path remained after quarantine, so HQA raised a systemic quench (`path_found: false`) rather than proposing a route through degraded qubits. Refusing to route is the correct fail-closed outcome here, and it is what HQA did.

## Constructive cat-qubit work
The affirmative cat-qubit results -- biased-noise routing on a routable fabric and the honest setpoint analysis -- live in `reports/HQA_CAT_BIASED_NOISE_ROUTER_V0.md` and `docs/HQA_CAT_QUBIT_COMPATIBILITY_NOTE_V0.md`.

## JSON Audit Log
```json
[
  {
    "timestamp": "2026-07-05T16:04:04.936426",
    "module": "SYSTEM",
    "event_type": "ALICE_BOB_INTEGRATION_START",
    "data": {
      "hardware_target": "CAT_QUBIT"
    }
  },
  {
    "timestamp": "2026-07-05T16:04:04.936426",
    "module": "FABRIC_SIMULATOR",
    "event_type": "INITIALIZE",
    "data": {
      "nodes": 13,
      "topology": "SPARSE_LATTICE",
      "grid_size": "5x5"
    }
  },
  {
    "timestamp": "2026-07-05T16:04:04.936426",
    "module": "FABRIC_SIMULATOR",
    "event_type": "CAT_QUBIT_MODE_ENGAGED",
    "data": {
      "bit_flip_suppression": "EXPONENTIAL",
      "phase_flip_vulnerability": "EXPOSED"
    }
  },
  {
    "timestamp": "2026-07-05T16:04:04.936426",
    "module": "FABRIC_SIMULATOR",
    "event_type": "FAULT_INJECTED",
    "data": {
      "node": "Q_1_1",
      "coherence": 0.1,
      "error_type": "PHASE_FLIP"
    }
  },
  {
    "timestamp": "2026-07-05T16:04:04.936426",
    "module": "FABRIC_SIMULATOR",
    "event_type": "FAULT_INJECTED",
    "data": {
      "node": "Q_3_3",
      "coherence": 0.1,
      "error_type": "PHASE_FLIP"
    }
  },
  {
    "timestamp": "2026-07-05T16:04:04.936426",
    "module": "FABRIC_SIMULATOR",
    "event_type": "ASYMMETRIC_STRESS_INJECTED",
    "data": {
      "faults": [
        {
          "node": "Q_1_1",
          "coherence": 0.1,
          "status": "UNSTABLE",
          "error_type": "PHASE_FLIP"
        },
        {
          "node": "Q_3_3",
          "coherence": 0.1,
          "status": "UNSTABLE",
          "error_type": "PHASE_FLIP"
        }
      ]
    }
  },
  {
    "timestamp": "2026-07-05T16:04:04.936426",
    "module": "SENTINEL",
    "event_type": "QUENCH_DECISION",
    "data": {
      "node": "Q_1_1",
      "reason": "coherence_critical",
      "coherence": 0.1
    }
  },
  {
    "timestamp": "2026-07-05T16:04:04.936426",
    "module": "SENTINEL",
    "event_type": "QUENCH_DECISION",
    "data": {
      "node": "Q_3_3",
      "reason": "coherence_critical",
      "coherence": 0.1
    }
  },
  {
    "timestamp": "2026-07-05T16:04:04.936426",
    "module": "QUARANTINE_MANAGER",
    "event_type": "NODE_ISOLATED",
    "data": {
      "node": "Q_1_1"
    }
  },
  {
    "timestamp": "2026-07-05T16:04:04.936426",
    "module": "QUARANTINE_MANAGER",
    "event_type": "NODE_ISOLATED",
    "data": {
      "node": "Q_3_3"
    }
  },
  {
    "timestamp": "2026-07-05T16:04:04.936426",
    "module": "HIPPOCAMPUS",
    "event_type": "ROUTING_REQUESTED",
    "data": {
      "start": "Q_0_0",
      "end": "Q_4_4"
    }
  },
  {
    "timestamp": "2026-07-05T16:04:04.936426",
    "module": "HIPPOCAMPUS",
    "event_type": "SYSTEMIC_QUENCH",
    "data": {
      "reason": "no_safe_path_found"
    }
  },
  {
    "timestamp": "2026-07-05T16:04:04.936426",
    "module": "SYSTEM",
    "event_type": "ALICE_BOB_INTEGRATION_COMPLETE",
    "data": {
      "path_found": false
    }
  }
]
```

## Boundary
Advisory simulation only. No hardware authority, no live Alice & Bob calibration data, no pulse or cryostat control. Node parameters are representative demo values. Demonstrates fail-closed abstention, not a physical routing or fidelity result.
