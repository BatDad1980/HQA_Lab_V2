# HQA Phase 9: Cross-Resonance Gate Routing Report

This report demonstrates HQA operating beyond single-path routing in a proxy scenario. The scheduler scans the sparse-lattice for a usable physical edge and asks the Hippocampus router to place two logical states near that pair for a simulated CR-gate workflow.

## JSON Audit Log
```json
[
  {
    "timestamp": "2026-06-14T22:44:40.480052",
    "module": "SYSTEM",
    "event_type": "CR_ROUTING_DEMO_START",
    "data": {
      "mode": "TWO_QUBIT_ENTANGLEMENT"
    }
  },
  {
    "timestamp": "2026-06-14T22:44:40.480052",
    "module": "FABRIC_SIMULATOR",
    "event_type": "INITIALIZE",
    "data": {
      "nodes": 13,
      "topology": "SPARSE_LATTICE",
      "grid_size": "5x5"
    }
  },
  {
    "timestamp": "2026-06-14T22:44:40.480052",
    "module": "FABRIC_SIMULATOR",
    "event_type": "FAULT_INJECTED",
    "data": {
      "node": "Q_2_2",
      "coherence": 0.1,
      "error_type": "DEGRADED"
    }
  },
  {
    "timestamp": "2026-06-14T22:44:40.480052",
    "module": "FABRIC_SIMULATOR",
    "event_type": "FAULT_INJECTED",
    "data": {
      "node": "Q_1_1",
      "coherence": 0.1,
      "error_type": "QUARANTINED"
    }
  },
  {
    "timestamp": "2026-06-14T22:44:40.480052",
    "module": "CR_SCHEDULER",
    "event_type": "ENTANGLING_GATE_REQUESTED",
    "data": {
      "logical_a": "Q_0_0",
      "logical_b": "Q_4_4"
    }
  },
  {
    "timestamp": "2026-06-14T22:44:40.480052",
    "module": "CR_SCHEDULER",
    "event_type": "TARGET_EDGE_SELECTED",
    "data": {
      "target_edge": [
        "Q_4_0",
        "Q_3_1"
      ]
    }
  },
  {
    "timestamp": "2026-06-14T22:44:40.480052",
    "module": "CR_SCHEDULER",
    "event_type": "MULTI_ROUTE_FAILED",
    "data": {
      "reason": "pathing_conflict"
    }
  },
  {
    "timestamp": "2026-06-14T22:44:40.480052",
    "module": "SYSTEM",
    "event_type": "CR_ROUTING_DEMO_COMPLETE",
    "data": {
      "success": false
    }
  }
]
```
