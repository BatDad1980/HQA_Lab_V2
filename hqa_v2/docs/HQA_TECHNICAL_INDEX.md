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
| `hqa_v2/integrations/hqa_risk_field_v0.py` | Converts topology, syndrome, and cascade evidence into an advisory risk field. |
| `hqa_v2/reports/HQA_RISK_FIELD_V0.md` | Risk-field ranking report. |
| `hqa_v2/quality/hqa_risk_field_gate.py` | Verifies risk-field ranking and advisory-only boundary. |
| `hqa_v2/reports/HQA_RISK_FIELD_GATE.md` | Risk-field gate report. |
| `hqa_v2/integrations/shadow_adaptive_proposal_v0.py` | Converts the risk field into quarantine, reroute, and HAL dry-run review artifacts. |
| `hqa_v2/reports/HQA_SHADOW_ADAPTIVE_PROPOSAL_V0.md` | Shadow adaptive proposal report. |
| `hqa_v2/quality/shadow_adaptive_proposal_gate.py` | Verifies adaptive proposal boundaries and manifest integrity. |
| `hqa_v2/reports/HQA_SHADOW_ADAPTIVE_PROPOSAL_GATE.md` | Shadow adaptive proposal gate report. |
| `hqa_v2/integrations/simulator_stress_schedule_v0.py` | Runs nominal, mild, correlated, and no-route-hold profiles through the risk/proposal chain. |
| `hqa_v2/reports/HQA_SIMULATOR_STRESS_SCHEDULE_V0.md` | Simulator stress schedule report. |
| `hqa_v2/quality/simulator_stress_schedule_gate.py` | Verifies stress-profile behavior, monotonic risk, and advisory boundaries. |
| `hqa_v2/reports/HQA_SIMULATOR_STRESS_SCHEDULE_GATE.md` | Simulator stress schedule gate report. |
| `hqa_v2/integrations/environment_profile_library_v0.py` | Translates Chaos-Worldmodel regime names into HQA advisory profile thresholds. |
| `hqa_v2/reports/HQA_ENVIRONMENT_PROFILE_LIBRARY_V0.md` | Environment profile library report. |
| `hqa_v2/quality/environment_profile_library_gate.py` | Verifies profile completeness, threshold ordering, and interpretation-only boundaries. |
| `hqa_v2/reports/HQA_ENVIRONMENT_PROFILE_LIBRARY_GATE.md` | Environment profile library gate report. |

## Cat-Qubit Lane

| Artifact | Purpose |
|---|---|
| `hqa_v2/integrations/cat_cascade_proxy.py` | Defines solver-ready cat-qubit cascade evidence contract. |
| `hqa_v2/reports/HQA_CAT_CASCADE_PROXY.md` | Cat-qubit proxy report. |
| `hqa_v2/integrations/cat_solver_contract_v0.py` | Defines the required solver evidence fields for QuTiP/Dynamiqs adapters. |
| `hqa_v2/reports/HQA_CAT_SOLVER_CONTRACT_V0.md` | Cat solver contract report. |
| `hqa_v2/quality/cat_solver_contract_gate.py` | Verifies solver contract completeness and no live authority. |
| `hqa_v2/reports/HQA_CAT_SOLVER_CONTRACT_GATE.md` | Cat solver contract gate report. |

Current status: QuTiP and Dynamiqs/JAX are available in the local environment. The current contract remains bounded and does not grant live hardware authority.

## Vendor Interface Lane

| Artifact | Purpose |
|---|---|
| `hqa_v2/integrations/external_quantum_trace_intake_v0.py` | Defines and exercises the external quantum trace intake front door. |
| `hqa_v2/reports/HQA_EXTERNAL_QUANTUM_TRACE_INTAKE_V0.md` | External quantum trace intake report. |
| `hqa_v2/quality/external_quantum_trace_intake_gate.py` | Verifies safe acceptance/rejection of external trace payloads. |
| `hqa_v2/reports/HQA_EXTERNAL_QUANTUM_TRACE_INTAKE_GATE.md` | External quantum trace intake gate report. |
| `hqa_v2/integrations/topology_compensation_profiles_v0.py` | Defines chip-family compensation profiles for heavy-hex, grid/lattice, bosonic/cat, and neutral graphs. |
| `hqa_v2/reports/HQA_TOPOLOGY_COMPENSATION_PROFILES_V0.md` | Topology compensation profile report. |
| `hqa_v2/quality/topology_compensation_profiles_gate.py` | Verifies topology-family coverage and normalized trace compensation metadata. |
| `hqa_v2/reports/HQA_TOPOLOGY_COMPENSATION_PROFILES_GATE.md` | Topology compensation profile gate report. |
| `hqa_v2/integrations/dual_vendor_test_matrix_v0.py` | Defines parallel cat-qubit and non-cat vendor testing lanes. |
| `hqa_v2/reports/HQA_DUAL_VENDOR_TEST_MATRIX_V0.md` | Dual vendor test matrix report. |
| `hqa_v2/quality/dual_vendor_test_matrix_gate.py` | Verifies test-lane coverage and claim boundaries. |
| `hqa_v2/reports/HQA_DUAL_VENDOR_TEST_MATRIX_GATE.md` | Dual vendor test matrix gate report. |
| `hqa_v2/integrations/legacy_scar_router_v0.py` | Rewrites the useful HQA V1 scar-router mechanism as deterministic shadow replay. |
| `hqa_v2/reports/HQA_LEGACY_SCAR_ROUTER_V0.md` | Legacy scar-router harvest report. |
| `hqa_v2/quality/legacy_scar_router_gate.py` | Verifies scar routing, phase-bias risk, safe holds, and no hardware authority. |
| `hqa_v2/reports/HQA_LEGACY_SCAR_ROUTER_GATE.md` | Legacy scar-router gate report. |
| `hqa_v2/integrations/legacy_autonomic_stress_regulator_v0.py` | Rewrites the useful HQA V1 vagus/autonomic stress primitive as advisory patch-state classification. |
| `hqa_v2/reports/HQA_LEGACY_AUTONOMIC_STRESS_REGULATOR_V0.md` | Legacy autonomic stress harvest report. |
| `hqa_v2/quality/legacy_autonomic_stress_regulator_gate.py` | Verifies stress bands, advisory actions, safe holds, and no live dispatch. |
| `hqa_v2/reports/HQA_LEGACY_AUTONOMIC_STRESS_REGULATOR_GATE.md` | Legacy autonomic stress gate report. |
| `hqa_v2/integrations/hqa_mud_run_v0.py` | Runs malformed, hostile, conflicting, and physically unusable payloads through HQA fail-closed logic. |
| `hqa_v2/reports/HQA_MUD_RUN_V0.md` | Mud-run breakpoint report. |
| `hqa_v2/quality/hqa_mud_run_gate.py` | Verifies expected rejection, quarantine, review-lock, safe-hold, and accept-shadow behavior. |
| `hqa_v2/reports/HQA_MUD_RUN_GATE.md` | Mud-run gate report. |
| `hqa_v2/integrations/cognitive_advisory_contract_v0.py` | Converts model-generated advisory outputs into bounded annotations under deterministic HQA gates. |
| `hqa_v2/reports/HQA_COGNITIVE_ADVISORY_CONTRACT_V0.md` | Cognitive advisory containment report. |
| `hqa_v2/quality/cognitive_advisory_contract_gate.py` | Verifies model advice cannot override gates, release secrets, or authorize hardware. |
| `hqa_v2/reports/HQA_COGNITIVE_ADVISORY_CONTRACT_GATE.md` | Cognitive advisory contract gate report. |
| `hqa_v2/integrations/bacl_entropy_policy_v0.py` | Replays the BACL entropy red-team finding: public telemetry alone must never regenerate manifest-signing authority. |
| `hqa_v2/reports/HQA_BACL_ENTROPY_POLICY_V0.md` | BACL entropy policy report. |
| `hqa_v2/quality/bacl_entropy_policy_gate.py` | Verifies the legacy deterministic-seed exploit and hardened private-salt mitigation. |
| `hqa_v2/reports/HQA_BACL_ENTROPY_POLICY_GATE.md` | BACL entropy policy gate report. |
| `hqa_v2/integrations/hqa_intervention_gate_v0.py` | Converts stress-run breakpoints into stand-down, monitor, remap, key-rotation, compression, and safe-hold policy. |
| `hqa_v2/reports/HQA_INTERVENTION_GATE_V0.md` | Intervention policy report. |
| `hqa_v2/quality/hqa_intervention_gate_quality.py` | Verifies stress-run breakpoints map to bounded shadow-policy decisions. |
| `hqa_v2/reports/HQA_INTERVENTION_GATE_QUALITY.md` | Intervention gate quality report. |
| `hqa_v2/integrations/telemetry_compression_gate_v0.py` | Compresses large telemetry payloads into bounded risk features before cognitive advisory review. |
| `hqa_v2/reports/HQA_TELEMETRY_COMPRESSION_GATE_V0.md` | Telemetry compression report. |
| `hqa_v2/quality/telemetry_compression_gate_quality.py` | Verifies compressed summaries preserve intervention decisions and fit latency budget. |
| `hqa_v2/reports/HQA_TELEMETRY_COMPRESSION_GATE_QUALITY.md` | Telemetry compression quality report. |
| `hqa_v2/integrations/patch_routing_prototype_v0.py` | Tests coarse patch routing as a bounded alternative to global node-level A* at large fabric sizes. |
| `hqa_v2/reports/HQA_PATCH_ROUTING_PROTOTYPE_V0.md` | Patch routing prototype report. |
| `hqa_v2/quality/patch_routing_prototype_quality.py` | Verifies patch routing reduces planning workload and preserves safe-hold behavior. |
| `hqa_v2/reports/HQA_PATCH_ROUTING_PROTOTYPE_QUALITY.md` | Patch routing quality report. |
| `hqa_v2/integrations/provider_normalization_matrix_v0.py` | Normalizes IBM, Braket, Azure, CUDA-Q, Cirq/qsim, and cat-solver telemetry dialects into one HQA shadow adapter grammar. |
| `hqa_v2/reports/HQA_PROVIDER_NORMALIZATION_MATRIX_V0.md` | Provider normalization matrix report. |
| `hqa_v2/quality/provider_normalization_matrix_gate.py` | Verifies provider coverage, topology-family coverage, source hashing, and no live authority. |
| `hqa_v2/reports/HQA_PROVIDER_NORMALIZATION_MATRIX_GATE.md` | Provider normalization matrix gate report. |
| `hqa_v2/integrations/backend_health_translator_v0.py` | Translates provider/backend calibration snapshots into one HQA health profile grammar. |
| `hqa_v2/reports/HQA_BACKEND_HEALTH_TRANSLATOR_V0.md` | Backend health translation report comparing Kingston and Fez through normalized health, not backend name. |
| `hqa_v2/quality/backend_health_translator_gate.py` | Verifies bounded health scores, backend-neutral policy, and honest spatial-clustering limitations. |
| `hqa_v2/reports/HQA_BACKEND_HEALTH_TRANSLATOR_GATE.md` | Backend health translator gate report. |
| `hqa_v2/integrations/ibm_backend_field_map_v0.py` | Defines the richer IBM field-map capture layer for per-qubit classes, edge-neighborhood risk, and degraded cluster proxy. |
| `hqa_v2/reports/HQA_IBM_BACKEND_FIELD_MAP_V0.md` | IBM field-map report. Default mode is offline fixture; live metadata capture is explicit opt-in and submits zero jobs. |
| `hqa_v2/quality/ibm_backend_field_map_gate.py` | Verifies field-map evidence shape, degraded reasons, edge-neighborhood risk, cluster proxy, and no hardware authority. |
| `hqa_v2/reports/HQA_IBM_BACKEND_FIELD_MAP_GATE.md` | IBM field-map gate report. |
| `hqa_v2/integrations/field_map_replay_v0.py` | Replays a backend field map into shadow quarantine candidates, reroute review, intervention hint, and hashed review artifacts. |
| `hqa_v2/reports/HQA_FIELD_MAP_REPLAY_V0.md` | Field-map replay report. |
| `hqa_v2/quality/field_map_replay_gate.py` | Verifies replay artifacts, bounded intervention mode, manifest integrity, and no hardware authority. |
| `hqa_v2/reports/HQA_FIELD_MAP_REPLAY_GATE.md` | Field-map replay gate report. |
| `hqa_v2/integrations/provider_replay_harness_v0.py` | Replays normalized provider packets through one deterministic HQA response grammar. |
| `hqa_v2/reports/HQA_PROVIDER_REPLAY_HARNESS_V0.md` | Provider replay harness report. |
| `hqa_v2/quality/provider_replay_harness_gate.py` | Verifies IBM, Braket, Azure, CUDA-Q, Cirq/qsim, and cat-solver lanes replay with bounded decisions and no live authority. |
| `hqa_v2/reports/HQA_PROVIDER_REPLAY_HARNESS_GATE.md` | Provider replay harness gate report. |
| `hqa_v2/demos/build_evidence_dashboard_v0.py` | Builds a static read-only dashboard from current HQA evidence logs and reports. |
| `hqa_v2/outputs/evidence_dashboard_v0/HQA_EVIDENCE_DASHBOARD_V0.html` | Generated evidence dashboard. |
| `hqa_v2/quality/evidence_dashboard_gate.py` | Verifies the dashboard is evidence-backed, non-interactive, and boundary-safe. |
| `hqa_v2/reports/HQA_EVIDENCE_DASHBOARD_GATE.md` | Evidence dashboard gate report. |
| `hqa_v2/docs/HQA_V1_LEGACY_HARVEST_INDEX.md` | Read-only harvest index for mechanisms pulled from the separate HQA V1 line. |
| `hqa_v2/docs/HQA_VENDOR_INTERFACE_CONTRACT.md` | Human-readable vendor interface contract. |
| `hqa_v2/schemas/*.schema.json` | Strict JSON schemas for topology, syndrome, quarantine, reroute, and HAL manifest payloads. |
| `hqa_v2/docs/HQA_REAL_QUANTUM_DATA_READINESS.md` | Path from local proxy evidence to authorized external quantum telemetry. |
| `hqa_v2/docs/HQA_EXTERNAL_RESULTS_TRIAGE_2026_06_01.md` | Internal triage of candidate IBM heavy-hex and cat-qubit result notes. |
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
| `hqa_v2/docs/HQA_CROSS_PROJECT_CLAIM_AUDIT.md` | Separates supported HQA evidence, valid concept transfer, and unsupported cross-project claims. |

## One-Command Check

From the repository root:

```powershell
python hqa_v2/quality/hqa_v2_regression_runner.py
python hqa_v2/quality/claim_boundary_smoke_test.py
```

## Boundary

HQA V2 should be evaluated as a controlled proxy and shadow-advisory architecture.

It is not a live quantum hardware controller.
