# HQA HAL Pump Hysteresis Contract Gate

## Purpose

This gate verifies that autonomic pump activation cannot be undone by stabilization logic in the same control tick.

## Results

- Checks: `12`
- Passed: `12`
- Failed: `0`

| Check | Status | Detail |
|---|---:|---|
| schema_version | PASS | Contract schema is V0. |
| local_control_policy_replay | PASS | Mode: `local_control_policy_replay`. |
| same_tick_deactivation_blocked | PASS | Same-tick activation/deactivation is blocked. |
| no_hardware_authority | PASS | No hardware authority granted. |
| no_real_actuator_authority | PASS | No real actuator authority granted. |
| stress_at_stable_temp_holds | PASS | Stress response holds even at stable temperature. |
| same_tick_stabilization_holds | PASS | Same-tick stabilization cannot undo new activation. |
| first_hold_tick_holds | PASS | First hold tick keeps pump active. |
| after_hold_deactivation_allowed | PASS | Deactivation is allowed after hold window. |
| high_temperature_activates_hold | PASS | High temperature activation enters hold. |
| policy_rule_mentions_hold | PASS | Policy rule declares minimum hold window. |
| boundary_blocks_actuation | PASS | Boundary blocks sockets and pump activation. |

## Boundary

This gate validates local pump-state policy only. It does not send SCPI commands, open sockets, activate pumps, or authorize HAL execution.
