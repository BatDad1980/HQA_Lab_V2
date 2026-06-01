# HQA V2 Technical Index

## Purpose

This index points a technical reviewer to the current HQA V2 evidence chain.

HQA V2 is a proxy control-plane laboratory. It demonstrates simulator-facing cascade observation, topology-aware quarantine/reroute logic, dry-run HAL boundaries, schema contracts, and shadow-mode packet generation.

It does not claim physical quantum hardware validation, production QEC performance, or live hardware control authority.

## Core Regression

| Artifact | Purpose |
|---|---|
| `hqa_v2/docs/HQA_REVIEWER_BRIEF.md` | High-level reviewer orientation and architecture diagram. |
| `hqa_v2/quality/hqa_v2_regression_runner.py` | Runs the safe HQA V2 regression suite. |
| `hqa_v2/reports/HQA_V2_REGRESSION_SUMMARY.md` | Latest regression summary. |
| `hqa_v2/quality/claim_boundary_smoke_test.py` | Scans text artifacts for forbidden overclaim language. |

## Simulator And Cascade Evidence

| Artifact | Purpose |
|---|---|
| `hqa_v2/integrations/simulator_readiness.py` | Checks optional simulator package availability. |
| `hqa_v2/reports/HQA_SIMULATOR_READINESS.md` | Simulator readiness report. |
| `hqa_v2/integrations/qiskit_cascade_observer.py` | Builds a Qiskit syndrome-history cascade observer. |
| `hqa_v2/reports/HQA_QISKIT_CASCADE_OBSERVER.md` | Qiskit cascade observer report. |
| `hqa_v2/integrations/qiskit_aer_cascade_noise_probe.py` | Runs a local Aer nominal/stress cascade-noise probe. |
| `hqa_v2/reports/HQA_QISKIT_AER_CASCADE_NOISE_PROBE.md` | Local Aer cascade-noise report. |
| `hqa_v2/quality/qiskit_aer_cascade_gate.py` | Verifies nominal/stress profile separation. |
| `hqa_v2/reports/HQA_QISKIT_AER_CASCADE_GATE.md` | Local Aer cascade gate report. |

## Cat-Qubit Lane

| Artifact | Purpose |
|---|---|
| `hqa_v2/integrations/cat_cascade_proxy.py` | Defines solver-ready cat-qubit cascade evidence contract. |
| `hqa_v2/reports/HQA_CAT_CASCADE_PROXY.md` | Cat-qubit proxy report. |

Current status: spec-only until QuTiP or Dynamiqs/JAX is installed.

## Vendor Interface Lane

| Artifact | Purpose |
|---|---|
| `hqa_v2/docs/HQA_VENDOR_INTERFACE_CONTRACT.md` | Human-readable vendor interface contract. |
| `hqa_v2/schemas/*.schema.json` | Strict JSON schemas for topology, syndrome, quarantine, reroute, and HAL manifest payloads. |
| `hqa_v2/quality/schema_contract_smoke_test.py` | Verifies schema presence and strictness. |
| `hqa_v2/reports/HQA_SCHEMA_CONTRACT_SMOKE.md` | Schema smoke-test report. |
| `hqa_v2/package/build_vendor_shadow_packet.py` | Generates a sample vendor shadow-mode handoff packet. |
| `hqa_v2/outputs/vendor_shadow_packet_v1/README.md` | Generated sample packet entry point. |
| `hqa_v2/quality/vendor_shadow_packet_validation.py` | Validates sample packet payloads and manifest hashes. |
| `hqa_v2/reports/HQA_VENDOR_SHADOW_PACKET_VALIDATION.md` | Packet validation report. |

## Hardware Boundary

| Artifact | Purpose |
|---|---|
| `hqa_v2/reports/HQA_HAL_CONTROL_BOUNDARY_REPORT.md` | HAL dry-run and rejection boundary evidence. |
| `hqa_v2/safety/hal_safety_governor.py` | Local HAL safety boundary logic. |
| `hqa_v2/safety/control_manifest.py` | Hardware-facing manifest structure. |

## Roadmap

| Artifact | Purpose |
|---|---|
| `hqa_v2/docs/HQA_MONSTER_PATH_ROADMAP.md` | Roadmap from proxy stack to simulator bridge, digital twin replay, shadow hardware, and controlled integration candidate. |
| `hqa_v2/docs/HQA_CHAOS_WORLD_MODEL_TRANSFER_MEMO.md` | Boundary-safe concept transfer from Chaos-Worldmodel principles into HQA risk-field design. |

## One-Command Check

From the repository root:

```powershell
python hqa_v2/quality/hqa_v2_regression_runner.py
python hqa_v2/quality/claim_boundary_smoke_test.py
```

## Boundary

HQA V2 should be evaluated as a controlled proxy and shadow-advisory architecture.

It is not a live quantum hardware controller.
