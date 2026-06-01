# HQA V1 Legacy Harvest Index

## Purpose

This index records what was worth harvesting from the separate `HQA_V1` line into the clean `HQA_LAB_V1` lane.

The goal is not to merge the projects. The goal is to preserve independent project evolution while translating useful mechanisms into clean, bounded, reviewer-safe artifacts.

## Source Boundary

The legacy repo was inspected as read-only.

Do not copy secrets, API keys, live credential paths, generated zip packets, or hype-heavy claims from the legacy repo into this clean lab.

## Harvest Now

| Legacy Source | Useful Mechanism | Clean Translation |
|---|---|---|
| `topological_memory.py` | A* routing with danger gradients around known faults. | `legacy_scar_router_v0.py` rewrites this as deterministic shadow replay. |
| `topology_mapper.py` | Heavy-hex-like sparse mask and structural voids. | Keep as topology-family inspiration; prefer schema-normalized vendor traces for real review. |
| `sentinel_reflex.py` | Local patch scanning, plastic threshold, quarantine handoff, micro-sleep. | Translate into patch-local risk scoring and calibration holds. |
| `qubit_fabric.py` | Error age, cascade threshold, quarantine, sleep zones, thermal zones. | Use as simulator-stress vocabulary, not as physical validation. |
| `vagus_nerve.py` and `hqa_v2/core/vagus_nerve_predictor.py` | Aggregate local stress and preemptive degradation detection. | Convert to advisory drift-momentum scores before quarantine proposals. |
| `hqa_v2/routing/hippocampus_router.py` | Graph-based risk scoring with phase-flip proximity penalty. | Aligns with cat-qubit profile compensation. |
| `hqa_v2/routing/cross_resonance_scheduler.py` | Select clean physical pairs before two-qubit gate scheduling. | Later port as a dry-run multi-route scheduler, not a live gate controller. |
| `hqa_v2/physics/microwave_pulse_shaper.py` | Crosstalk-aware pulse envelope metadata. | Later port as pulse-review manifest only. No direct pulse authority. |
| `hqa/qec/surface_code.py` | Minimal surface-code syndrome and Sentinel hook. | Later port as a toy QEC adapter behind the same external trace contract. |

## Harvest Later

1. Patch-local stress aggregation: turn micro-sleep and stress thresholds into a deterministic calibration-hold lane.
2. Multi-route scheduler: prove two logical routes can be proposed without crossing quarantined/scarred zones.
3. Surface-code adapter: convert toy syndromes into the existing `syndrome_record` schema.
4. Pulse review manifest: generate DRAG/Gaussian-style metadata for review without hardware execution.
5. Drift-momentum gate: use short history windows to identify fast coherence collapse before a threshold breach.

## Quarantine

| Legacy Pattern | Reason |
|---|---|
| `apikey.json` and hardcoded `Z:\...apikey.json` references | Secret-handling risk. Use environment variables and redacted exported traces only. |
| `.env` loading from personal project paths | Not clean-lab reproducible and may expose private paths. |
| "God Protocol", "100% cascade prevention", "infinite scalability", and "proves conclusively" language | Buyer/reviewer liability and unsupported overclaim framing. |
| Mock physical HAL network calls | Useful for private lab demos, but clean lab should remain dry-run unless a vendor grants explicit test authority. |
| Generated zip packets from legacy line | Preserve separately; do not mix into clean lab evidence. |

## First Clean Harvest

`hqa_v2/integrations/legacy_scar_router_v0.py` now captures the V1 scar-router mechanism as a clean artifact.

It demonstrates:

- hard avoidance of quarantined nodes
- hard avoidance of sleep/calibration holds
- structural void handling
- scar-risk gradients around damaged nodes
- cat-qubit phase-flip proximity penalty
- `SAFE_HOLD` when no route exists
- no live hardware authority

The paired gate is `hqa_v2/quality/legacy_scar_router_gate.py`.

## Reviewer Boundary

This harvest does not claim physical quantum hardware validation, production QEC performance, pulse calibration authority, or live HAL control.

It is a controlled mechanism translation from one independent project branch into the clean HQA V2 evidence chain.
