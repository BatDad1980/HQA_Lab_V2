# HQA Jedi Harvest Map

Date: 2026-06-04

## Purpose

This document classifies useful material from the Quantum_Jedi HQA lane for possible import into the clean HQA lane.

Clean target:

`X:\HQA_LAB_V1`

Storm/source lane:

`Z:\Homeostatic_Quantum_Architecture\Quantum_Jedi`

This is a clean-room map, not an automatic merge plan. Nothing from the source lane should be buyer-facing until it passes claim, credential, and wording review.

## Intake Summary

Quantum_Jedi is technically valuable. It has:

- 87 passing local tests,
- intervention-gate logic,
- BACL red-team and hardened key policy work,
- boundary gateway / HAL safety logic,
- cryostat telemetry simulation and regulation,
- IBM calibration validation reports,
- cat-qubit proxy validation reports,
- MWPM / QEC decoder boundary tests,
- telemetry server and dashboard work,
- evidence builder and report packaging work.

The repo is also clearly a storm-lane development environment. It includes hotter language, root-level artifacts, duplicated package surfaces, advisory-model experiments, and report metadata that needs reconciliation before external review.

## Clean-Lane Regression Status

After intake, the clean HQA lane was checked with:

`python hqa_v2\quality\hqa_v2_regression_runner.py`

Result:

`Passed 78/78 checks.`

This matters because many of the strongest Quantum_Jedi ideas already exist in the clean lane as bounded reports, local policy proofs, and quality gates. The current priority is therefore not a wholesale code import. The priority is report normalization, buyer packet curation, and selective mechanism comparison.

Clean-lane mechanisms already present include:

- BACL entropy policy proof.
- BACL fail-closed authority contract.
- Intervention gate quality checks.
- QEC decoder boundary partner policy.
- HAL pump hysteresis contract.
- Cognitive advisory non-authority contract.
- Telemetry compression gate.
- Provider replay harness.
- IBM live validation abstention replay.
- Evidence dashboard gate.

## Disposition Legend

- `HARVEST`: Bring forward into the clean lane with minimal rewrite.
- `REFRAME`: Keep the concept or evidence, but rewrite language and/or boundaries.
- `QUARANTINE`: Internal-only. Useful for thinking, not buyer-facing.
- `IGNORE`: Duplicate, outdated, or not useful for the clean lane.

## High-Value Harvest Candidates

| Source Area | Disposition | Reason | Clean-Lane Action |
|---|---:|---|---|
| `hqa/homeostatic/intervention_gate.py` | HARVEST | Clear deterministic mode selection: `NO_INTERVENTION`, `MONITOR_ONLY`, `SHADOW_REMAP`, `QUARANTINE_REMAP`, `SAFE_HOLD`. Strong abstention/intervention boundary. | Compare with X gate logic and port threshold hierarchy if absent. |
| `tests/test_intervention_gate.py` | HARVEST | Boundary coverage for healthy, drift, shadow, quarantine, and hold modes. | Adapt into X test suite. |
| `hqa/safety/boundary_gateway.py` | HARVEST / REFRAME | Strong SCPI whitelist, envelope checking, rate limits, and `SAFE_HOLD`. Some wording implies physical execution. | Port policy logic; rewrite all execution docs as dry-run/vendor-interface unless proven otherwise. |
| `tests/test_boundary_safety.py` | HARVEST | Validates hard control boundary behavior. | Adapt into X safety tests. |
| `hqa/safety/bacl.py` | HARVEST / REFRAME | Lamport OTS, single-use enforcement, HKDF-like salt hardening. Needs stronger secret-management boundary. | Port hardened policy; avoid biometric wording and default salt in buyer docs. |
| `benchmarks/entropy_red_team.py` | HARVEST | Excellent red-team proof that deterministic telemetry seeding fails and salted derivation blocks forgery. | Convert into clean report/test artifact. |
| `tests/test_bacl.py` | HARVEST | Verifies BACL core behavior. | Adapt into X suite. |
| `hqa/homeostatic/classical_hardware.py` | HARVEST / REFRAME | Cryostat telemetry loopback and dynamic telemetry modeling. | Port as mock/lab-interface simulation only. |
| `hqa/homeostatic/vagus_nerve.py` | HARVEST / REFRAME | Autonomic feedback and key rotation concept is useful. | Import feedback regulation only after command boundary review. |
| `tests/test_cryo_telemetry.py` | HARVEST | Strong regression for telemetry and regulation loop. | Adapt into X if HAL simulation exists. |
| `hqa/decoders/mwpm_decoder.py` | HARVEST | Practical QEC decoder boundary/matching logic. | Compare with X decoder; port bug fixes and boundary partner logic. |
| `tests/test_mwpm_decoder.py` | HARVEST | Verifies MWPM crash prevention. | Adapt into X. |
| `hqa/qec/surface_code.py` | HARVEST | Useful surface-code test scaffold. | Review for clean abstraction and import only stable pieces. |
| `hqa/validation/real_device_validation.py` | HARVEST / REFRAME | IBM calibration intake, degraded-qubit detection, and report shaping are valuable. | Reconcile with X provider-normalization logic; ensure no live job submission by default. |
| `hqa/validation/cat_device_validation.py` | HARVEST / REFRAME | Cat-qubit proxy model and optimizer are useful as proxy validation. | Preserve as proxy only; do not claim physical cat state validation. |
| `hqa/packaging/evidence_builder.py` | REFRAME | Good packaging idea, but current builder rewrites claim docs and has stale/inconsistent metadata. | Rebuild clean packager in X rather than copy directly. |
| `hqa_telemetry_server.py` | HARVEST / REFRAME | Telemetry/dashboard server useful for demos. | Import only after security, port, and no-network-by-default review. |
| `HQA_DASHBOARD.html` | REFRAME | Strong visual surface, but should be regenerated from clean data. | Use as design reference, not source of truth. |

## Report Harvest Candidates

| Source Report | Disposition | Notes |
|---|---:|---|
| `reports/CLAIMS_BOUNDARY.md` | REFRAME | Useful structure. Needs alignment with X claim-boundary language. |
| `reports/known_limitations.md` | HARVEST / REFRAME | Good limitations list. Needs metadata check and stronger distinction between simulation and physical validation. |
| `reports/hardware_validation/ibm_*.md` | HARVEST / REFRAME | Valuable IBM calibration evidence. Must reconcile backend qubit counts and snapshot dates. |
| `reports/hardware_validation/cat_qubit_results.md` | HARVEST / REFRAME | Useful proxy evidence. Must state analytical/proxy scope clearly. |
| `reports/safety_validation/boundary_safety.md` | HARVEST | Good buyer-facing safety report candidate after wording pass. |
| `reports/safety_validation/hal_control.md` | REFRAME | Useful but must avoid sounding like direct cryostat ownership. |
| `reports/safety_validation/topology_routing.md` | HARVEST | Strong and relevant. |
| `reports/stress_test_results.md` | REFRAME | Useful stress coverage, but language must be toned down. |
| `reports/benchmark_results.md` | REFRAME | Contains valuable scale experiments, but phrases like "100% cascade prevention", "scales perfectly", and "God Protocol" must not ship. |
| `reports/SHA256SUMS` | HARVEST | Good manifest pattern. Regenerate in X for clean package. |

## Quarantine Candidates

| Source Area | Reason |
|---|---|
| Root-level `HQA_V2_TECHNICAL_EVALUATION_PACKET.zip` | Generated package from storm lane. Do not ship directly. Rebuild from X. |
| Root-level `ibm_hardware_cache.json` | Cache artifact. Potentially useful internally, not buyer-facing. |
| Root-level `worldmodel.log` | Log artifact. Internal only. |
| `scratch/` | Internal experiments. |
| Advisory model traces with external LLM involvement | Useful for internal review, but not authority-bearing. |
| Any "monster", "God Protocol", or dramatic stress-test language | Internal only until reframed. |

## Specific Cleanup Risks

### Credential Hygiene

The source lane no longer contains `apikey.json`, and the provider was changed to use environment variables or explicit external key-file override.

Still enforce:

- no credentials in repo,
- no committed local key paths,
- no buyer packet containing token/CRN/API strings,
- no generated logs containing secret material.

### Report Metadata Drift

The report index in the source lane has shown backend metadata that may conflict with later live snapshots.

Clean lane must verify:

- backend name,
- qubit count,
- snapshot date,
- whether data is live, cached, or replayed,
- whether jobs were submitted,
- whether the result is calibration-only or execution evidence.

### Massive-Scale Simulation Language

Keep the evidence. Reframe the claim.

Use:

> Large-scale simulation demonstrates bounded local-control behavior under the simplified fault model.

Avoid:

> Scales perfectly.

Avoid:

> 100% cascade prevention.

Avoid:

> Solves quantum error correction.

### HAL / Cryostat Language

Use:

> loopback simulation,
> mock cryostat,
> vendor-interface scaffold,
> bounded command manifest,
> dry-run safety envelope.

Avoid:

> direct mechanical control,
> production cryostat ownership,
> autonomous physical actuation.

### LLM Advisory Boundary

The advisory layer is allowed to summarize and recommend.

It must never authorize.

Clean phrase:

> Advisory output is informational. Deterministic intervention gates, BACL, and HAL boundary checks remain authoritative.

## Recommended Import Order

1. Intervention gate and tests.
2. BACL entropy hardening and red-team test.
3. Boundary gateway policy and tests.
4. Cryostat telemetry mock and tests.
5. MWPM decoder boundary fix and tests.
6. IBM validation report normalization.
7. Cat-qubit proxy report normalization.
8. Clean evidence packager.
9. Dashboard regeneration from clean logs.

## Fresh Buyer Packet Requirements

A fresh HQA packet should include:

- reviewer brief,
- claim boundary,
- known limitations,
- IBM calibration snapshots,
- cat-qubit proxy report,
- topology routing evidence,
- HAL boundary safety report,
- intervention gate report,
- BACL red-team report,
- regression summary,
- manifest with SHA256 hashes,
- no source code unless under technical MNDA,
- no credentials,
- no raw caches,
- no dramatic internal language.

## Recommendation

Do not merge Quantum_Jedi wholesale.

Harvest it like a lab notebook:

- preserve the strong technical mechanisms,
- rewrite the claim boundary,
- regenerate evidence from clean code,
- stage only curated reports and manifests.

That gives HQA the best of both worlds: storm-lane creativity and clean-room credibility.
