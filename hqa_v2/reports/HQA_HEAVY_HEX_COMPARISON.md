# HQA Heavy-Hex Router Comparison Report

**Generated:** 2026-06-25T19:20:44Z  
**Test:** Generic BFS Router (baseline) vs HeavyHexRouter (physics-correct)  
**Data source:** Real IBM backend calibration snapshots (ibm_kingston, ibm_fez)  
**Authority:** Advisory only — no live hardware access, no jobs submitted

---

> **Methodology caveat — do not cite this as a routing-quality comparison.**
> The generic BFS baseline returns `NO PATH` on 13 of 15 routes, so its "0 degraded
> hits" and every "Winner: Generic" verdict are artifacts of *failing to route at
> all*, not of avoiding degraded qubits. The summary line "degraded hit reduction:
> −20 fewer" is therefore misleading and is **not** evidence that the generic router
> is better. The only defensible content here is that the HeavyHexRouter's A* physics
> cost model found valid weighted paths on the heavy-hex unit cell where the naive
> BFS found none. A fair head-to-head needs a baseline that actually returns paths;
> until then treat this as a work-in-progress method note, not headline evidence.

---

## Backend: `ibm_kingston`

### Real Calibration Snapshot

| Metric | Value |
|---|---|
| Qubits | 156 |
| Coupling edges (full chip) | 352 |
| Mean T1 | 168.9 µs |
| Mean T2 | 119.2 µs |
| Mean readout error | 0.0211 |
| Degraded qubits (full chip) | 33 (21.2%) |
| Degraded IDs in test slice | [2, 8] |

### Route Comparison (13-qubit heavy-hex unit cell)

| Route | Label | Generic Path | Generic Hits | HH Path | HH Hits | Winner |
|---|---|---|---|---|---|---|
| 0→11 | cross-chip long path | NO PATH | none | 0 → 1 → 2 → 3 → 6 → 10 → 11 | 2 | Generic |
| 0→4 | top row horizontal | NO PATH | none | 0 → 1 → 2 → 3 → 4 | 2 | Generic |
| 7→12 | bottom-left to bottom-anchor | NO PATH | none | 7 → 8 → 9 → 12 | 8 | Generic |
| 4→12 | right side diagonal | 4 → 3 → 6 → 10 → 9 → 12 | none | 4 → 3 → 6 → 10 → 9 → 12 | none | **HeavyHex** |
| 0→12 | corner to corner | NO PATH | none | 0 → 1 → 5 → 8 → 9 → 12 | 8 | Generic |

### Physics Cost Breakdown

| Route | Generic Cost (hops) | HeavyHex Physics Cost | Delta |
|---|---|---|---|
| 0→11 | N/A | 11.226 | N/A |
| 0→4 | N/A | 10.1758 | N/A |
| 7→12 | N/A | 9.6507 | N/A |
| 4→12 | 5.0 | 2.6255 | -2.3745 |
| 0→12 | N/A | 10.7009 | N/A |

---

## Backend: `ibm_fez`

### Real Calibration Snapshot

| Metric | Value |
|---|---|
| Qubits | 156 |
| Coupling edges (full chip) | 352 |
| Mean T1 | 152.6 µs |
| Mean T2 | 106.2 µs |
| Mean readout error | 0.0281 |
| Degraded qubits (full chip) | 61 (39.1%) |
| Degraded IDs in test slice | [1, 3, 6, 9, 11] |

### Route Comparison (13-qubit heavy-hex unit cell)

| Route | Label | Generic Path | Generic Hits | HH Path | HH Hits | Winner |
|---|---|---|---|---|---|---|
| 0→11 | cross-chip long path | NO PATH | none | 0 → 1 → 5 → 8 → 9 → 10 → 11 | 1, 9 | Generic |
| 0→4 | top row horizontal | NO PATH | none | 0 → 1 → 2 → 3 → 4 | 1, 3 | Generic |
| 7→12 | bottom-left to bottom-anchor | NO PATH | none | 7 → 8 → 9 → 12 | 9 | Generic |
| 4→12 | right side diagonal | NO PATH | none | 4 → 3 → 6 → 10 → 9 → 12 | 3, 6, 9 | Generic |
| 0→12 | corner to corner | NO PATH | none | 0 → 1 → 5 → 8 → 9 → 12 | 1, 9 | Generic |

### Physics Cost Breakdown

| Route | Generic Cost (hops) | HeavyHex Physics Cost | Delta |
|---|---|---|---|
| 0→11 | N/A | 27.3807 | N/A |
| 0→4 | N/A | 18.282 | N/A |
| 7→12 | N/A | 9.6692 | N/A |
| 4→12 | N/A | 26.8525 | N/A |
| 0→12 | N/A | 18.8102 | N/A |

---

## Backend: `ibm_marrakesh`

### Real Calibration Snapshot

| Metric | Value |
|---|---|
| Qubits | 156 |
| Coupling edges (full chip) | 352 |
| Mean T1 | 155.0 µs |
| Mean T2 | 110.0 µs |
| Mean readout error | 0.0250 |
| Degraded qubits (full chip) | 55 (35.3%) |
| Degraded IDs in test slice | [2, 5, 9, 11] |

### Route Comparison (13-qubit heavy-hex unit cell)

| Route | Label | Generic Path | Generic Hits | HH Path | HH Hits | Winner |
|---|---|---|---|---|---|---|
| 0→11 | cross-chip long path | NO PATH | none | 0 → 1 → 2 → 3 → 6 → 10 → 11 | 2 | Generic |
| 0→4 | top row horizontal | NO PATH | none | 0 → 1 → 2 → 3 → 4 | 2 | Generic |
| 7→12 | bottom-left to bottom-anchor | NO PATH | none | 7 → 8 → 9 → 12 | 9 | Generic |
| 4→12 | right side diagonal | NO PATH | none | 4 → 3 → 6 → 10 → 9 → 12 | 9 | Generic |
| 0→12 | corner to corner | NO PATH | none | 0 → 1 → 5 → 8 → 9 → 12 | 5, 9 | Generic |

### Physics Cost Breakdown

| Route | Generic Cost (hops) | HeavyHex Physics Cost | Delta |
|---|---|---|---|
| 0→11 | N/A | 19.2859 | N/A |
| 0→4 | N/A | 10.1906 | N/A |
| 7→12 | N/A | 9.6634 | N/A |
| 4→12 | N/A | 10.7178 | N/A |
| 0→12 | N/A | 18.7996 | N/A |

---

## Summary

| Metric | Generic Router | HeavyHexRouter |
|---|---|---|
| Total degraded qubit hits in paths | 0 | 20 |
| Routes tested | 15 | 15 |
| Degraded hit reduction | — | **-20 fewer** |

### What the Physics Cost Means

The generic router counts hops only — it has no concept of idle decoherence,
coupling-edge two-qubit gate error, or degraded-qubit quarantine proximity.

The HeavyHexRouter A* cost function accumulates:
- `IDLE_DECOHERENCE_PER_HOP = 0.5` per edge traversed
- `coupling_edge_error × 10` for each two-qubit gate on that edge
- `DEGRADED_SELF = 8.0` quarantine penalty for landing on a degraded qubit
- `QUARANTINE_PROXIMITY = 4.0` for qubits adjacent to degraded nodes

A higher physics cost = higher expected decoherence and gate error on that path.
The HeavyHexRouter trades hop count for error budget — the physically correct tradeoff.

---

**Boundary:** This is a calibration-derived simulation using real IBM backend
parameters projected onto a 13-qubit heavy-hex unit cell. It is not a live QPU
result, does not submit jobs, and does not grant HQA hardware authority.
Results are advisory only and suitable for IV&V review.

*Report hash: 86fbf2701b0bd3f3*