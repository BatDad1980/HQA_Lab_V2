# HQA Legacy Scar Router V0

## Purpose

This report records the first clean-lab harvest from the older HQA V1 line.

The useful mechanism is the Hippocampus-style scar router: a pathfinder that treats quarantined nodes, sleeping calibration zones, structural voids, and nearby damage as routing constraints.

## Results

| Scenario | Result | Detail |
|---|---:|---|
| Scarred sparse grid | `PROPOSE_REROUTE` | Path `['Q_0_1', 'Q_1_1', 'Q_2_1', 'Q_3_1', 'Q_3_2', 'Q_3_3', 'Q_4_3']` with cost `17.2`. |
| Cat phase bias | `ADVISORY_RISK_REWEIGHT` | Phase-flip cost `18.8` vs generic cost `13.2`. |
| No-route barrier | `SAFE_HOLD` | Barrier produced path `None`. |

## Harvested Pattern

- V1 `Hippocampus` danger gradients become a vendor-neutral scar-risk field.
- V1 sleep zones become temporary calibration holds.
- V1 quarantined nodes become hard routing walls.
- Cat-qubit phase-flip proximity gets a higher advisory cost than generic damage.

## Boundary

This artifact ports a legacy routing pattern into deterministic shadow replay. It does not validate physical quantum hardware, alter pulses, or dispatch HAL commands.
