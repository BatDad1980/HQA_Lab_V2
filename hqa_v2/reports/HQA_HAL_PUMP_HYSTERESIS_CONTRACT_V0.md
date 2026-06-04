# HQA HAL Pump Hysteresis Contract V0

## Purpose

This contract prevents a same-cycle contradiction in the autonomic cooling loop: a stress response cannot activate a pump and then immediately deactivate it in the same tick because the pre-action temperature was already stable.

## Summary

- Execution mode: `local_control_policy_replay`
- Minimum hold ticks: `1`
- Same-tick activation/deactivation allowed: `False`
- Hardware authority: `False`
- Real actuator authority: `False`

| Case | Decision | Reason |
|---|---|---|
| `stress_at_stable_temperature` | `PUMP_ON_HOLD` | `ACTIVATION_HOLDS_FOR_MINIMUM_WINDOW` |
| `new_activation_same_tick_stabilization_attempt` | `PUMP_ON_HOLD` | `ACTIVATION_HOLDS_FOR_MINIMUM_WINDOW` |
| `active_pump_first_hold_tick` | `PUMP_ON_HOLD` | `STABILIZED_BUT_HOLD_WINDOW_ACTIVE` |
| `active_pump_after_hold_window` | `PUMP_OFF_ALLOWED` | `STABILIZED_AFTER_HOLD_WINDOW` |
| `high_temperature_no_prior_pump` | `PUMP_ON_HOLD` | `ACTIVATION_HOLDS_FOR_MINIMUM_WINDOW` |

## Policy Rule

A pump activated by stress or high temperature must hold for at least one control tick before stabilization logic may deactivate it.

## Boundary

This contract models pump-state policy only. It opens no sockets, sends no SCPI commands, activates no pumps, and grants no HAL or actuator authority.
