# HQA Cross-Project Claim Audit

## Purpose

This memo audits a cross-project synthesis that initially looked like a hallucination.

The corrected finding:

> The synthesis was not pure hallucination. It blended real older HQA benchmark artifacts, real HQA/HPP biological-control concepts, and unsupported cross-project integration claims.

This memo separates those categories so the useful signal can be preserved without contaminating the clean HQA V2 lane.

## Source Categories

### Category A: Supported By Older HQA V1 / Root-Level Artifacts

These ideas appear in older HQA files at the repository root.

Examples:

- Localized Sentinel Reflex.
- Quenching anomalies before cascade.
- `-1` / isolated-node style scar behavior.
- Large simulated grids.
- 5,000,000 injected hardware faults in the Rust billion-cell benchmark.
- Traditional-decoder remaining error counts near 772 million in the older 1-billion-cell simulation report.
- O(1)-style local patch memory framing.
- Rust bare-metal simulation path.

Representative source files:

- `HQA_MASSIVE_SCALE_RESULTS.md`
- `HQA_BENCHMARK_REPORT.md`
- `HQA_V2_ROADMAP.md`
- `benchmark_suite.py`
- `v2_cuda_engine/benchmark_suite_cuda.py`
- `v3_rust_firmware/src/main.rs`

Boundary:

These are simulation artifacts and older internal reports. They should not be presented as physical quantum hardware validation.

### Category B: Supported As HQA V2 Clean-Lane Concepts

These ideas are now represented in the cleaner HQA V2 lane.

Examples:

- Quarantine of degraded nodes.
- Topology-aware reroute proposals.
- Syndrome-history cascade observation.
- Local Aer nominal/stress cascade profile separation.
- Cat-qubit proxy contract.
- Vendor shadow-mode schemas.
- HAL dry-run manifest boundary.

Representative source files:

- `hqa_v2/reports/HQA_QISKIT_AER_CASCADE_GATE.md`
- `hqa_v2/reports/HQA_CAT_CASCADE_PROXY.md`
- `hqa_v2/docs/HQA_VENDOR_INTERFACE_CONTRACT.md`
- `hqa_v2/reports/HQA_VENDOR_SHADOW_PACKET_VALIDATION.md`
- `hqa_v2/docs/HQA_REVIEWER_BRIEF.md`

Boundary:

These are controlled proxy, simulator, and shadow-advisory artifacts. They are cleaner than the older V1 language, but still do not prove physical hardware behavior.

### Category C: Valid As Architecture Transfer, Not Evidence Transfer

These ideas are useful if framed as shared biological control patterns.

Examples:

- HQA and HPP both use homeostatic regulation ideas.
- Damaged-area isolation in HQA can inspire cognitive-immune scar logic in HPP.
- Vagus/reflex/quarantine/reroute metaphors can transfer across systems.
- HPP can harvest HQA-style control organs without merging products.

Allowed phrasing:

> HPP and HQA remain separate systems, but both use a biological regulation pattern: baseline, rupture, reflex, quarantine, reroute, repair.

Forbidden phrasing:

> HPP proves HQA.

> HQA powers HPP.

> HPP controls HQA.

### Category D: Unsupported Or Contaminated

These claims should not be used unless new evidence is built.

Unsupported examples:

- Grace Blackwell cluster handoff.
- Blackwell nodes running HPP to verify HQA.
- HPP V5 as the logical computation layer for HQA.
- HPP Python orchestrator handshaking with a Rust HQA binary on Blackwell nodes.
- "It does not matter if there are 100 or 1 billion qubits" as a real-world claim.
- "Infinite fabric" or "perfectly scales" as external language.
- Any statement that older grid simulations equal physical 1-billion-qubit quantum hardware validation.

Boundary:

These may be useful as future integration concepts, but they are not current evidence.

## Revised Claim Map

| Claim Family | Status | Safe Framing |
|---|---|---|
| Sentinel local reflex | Supported in simulation | HQA tests localized proxy fault response. |
| O(1) patch memory | Supported as model design | HQA uses bounded local patch state in simulation. |
| 5M injected faults | Supported in older Rust simulation | Older V1-style benchmark injected 5M simulated faults into a 1B-cell grid. |
| 772M+ traditional errors | Supported in older report | Older simulation reported 772M+ remaining errors for the traditional baseline. |
| 0 HQA errors | Supported only inside that simulation model | Report as model outcome, not physical proof. |
| HQA immune/scar metaphor | Supported as architecture metaphor | HQA isolates degraded nodes and reroutes around them in proxy scenarios. |
| HPP/HQA shared biology | Valid concept transfer | Shared biological regulation pattern, separate evidence lanes. |
| HPP controlling HQA | Unsupported | Future concept only, not current architecture. |
| Blackwell integration | Unsupported | Do not claim. |
| Physical quantum validation | Unsupported | Do not claim. |

## Important Correction

The earlier judgment "this was just hallucination" was too blunt.

Better judgment:

> The synthesis was a contaminated blend. It correctly noticed real HQA patterns and some real old benchmark numbers, but it overstated the evidence and invented cross-system integration.

That means it should be mined, not trusted.

## Clean External Summary

Use this:

> HQA includes older large-scale simulation experiments and a newer cleaner V2 proxy lane. The strongest current position is not that HQA has been physically validated on quantum hardware, but that it implements a repeatable, local fault-response architecture with simulator evidence, syndrome-history capture, quarantine/reroute proposals, dry-run HAL boundaries, and vendor shadow-mode schemas.

Do not use this:

> HQA solved billion-qubit QEC or scales infinitely.

## Next Recommended Cleanup

The root-level HQA files contain older language that is exciting but too strong for external review.

Recommended actions:

1. Mark older root reports as historical/internal.
2. Add a non-claim disclaimer to root-level benchmark reports.
3. Keep `hqa_v2` as the clean reviewer lane.
4. If sharing the repo, direct reviewers to `README.md` and `hqa_v2/docs/HQA_REVIEWER_BRIEF.md`.
5. Do not remove old evidence yet; preserve it, but label it correctly.

## Final Principle

Do not throw away the strange signal.

Do not let the strange signal write the claim.

Mine it, verify it, bound it, and then decide what becomes architecture.
