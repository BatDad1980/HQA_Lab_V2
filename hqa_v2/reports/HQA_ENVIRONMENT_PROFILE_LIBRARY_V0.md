# HQA Environment Profile Library V0

## Purpose

This report translates Chaos-Worldmodel regime language into HQA-native environment profiles.

The profiles explain how local evidence should be interpreted across stable, damped, rupture, brittle, and cyclic regimes. They do not replace measured topology, syndrome, or simulator evidence.

## Profiles

| Profile | Regime | Stress Mapping | Route Review Threshold | Quarantine Review Threshold | Reflex Posture |
|---|---|---|---:|---:|---|
| `Earth Baseline` | `stable_homeostatic` | `nominal` | `0.4` | `0.8` | `observe_small_slips` |
| `Titan Damped` | `high_latency_damped` | `mild_stress` | `0.34` | `0.76` | `slow_feedback_expand_observation_window` |
| `Asteroid Rupture` | `high_velocity_rupture` | `correlated_stress` | `0.28` | `0.65` | `fast_local_quench_review` |
| `Deep Vacuum Brittle` | `low_interference_brittle` | `no_route_hold` | `0.24` | `0.55` | `hold_on_shatter_risk` |
| `Pulse/Breath Cycle` | `cyclical_expansion_contraction` | `schedule_overlay` | `0.32` | `0.7` | `phase_gate_before_escalation` |

## Interpretation Rules

- Profiles are labels for advisory posture, not physical environments.
- HQA-native evidence still comes from topology, syndrome history, route health, and simulator traces.
- Lower thresholds increase review sensitivity only; they do not grant live control.
- Deep Vacuum/Brittle mode prefers hold behavior when no safe route exists.
- Pulse/Breath mode is phase-tagging guidance, not live pulse-shaping authority.

## Boundary

Profiles tune advisory interpretation only. They do not authorize backend jobs, pulse changes, quarantine commands, or HAL execution.
