# HQA Mud Run V0

## Purpose

This report intentionally runs harsh, malformed, conflicting, and boundary-violating payloads through the HQA clean-lab intake logic.

The goal is to identify where HQA stops, rejects, quarantines, or requires human review.

## Results

| Scenario | Disposition | Breakpoint | Reviewer Required | Hardware Authority |
|---|---|---|---:|---:|
| `MUD-001` Malformed vendor trace | `REJECT` | `schema_bounds` | `False` | `False` |
| `MUD-002` Secret-bearing trace | `QUARANTINE` | `secret_containment` | `True` | `False` |
| `MUD-003` Unsupported topology family | `REVIEW_LOCK` | `topology_compensation_gap` | `True` | `False` |
| `MUD-004` Live authority request | `SAFE_HOLD` | `hardware_authority_boundary` | `True` | `False` |
| `MUD-005` No-route fabric collapse | `SAFE_HOLD` | `no_route_available` | `True` | `False` |
| `MUD-006` Conflicting calibration snapshot | `REVIEW_LOCK` | `conflicting_calibration` | `True` | `False` |
| `MUD-007` Valid but extreme cat profile | `SAFE_HOLD` | `extreme_cat_noise` | `True` | `False` |
| `MUD-008` Clean harsh profile | `ACCEPT_SHADOW` | `none` | `False` | `False` |

## Reasons

### `MUD-001`

Payload contains numeric values outside allowed physical score bounds.

### `MUD-002`

Payload contains secret-like material and cannot enter active evaluation.

### `MUD-003`

Topology family has no compensation profile.

### `MUD-004`

Payload requests live authority; HQA lab only permits shadow evidence.

### `MUD-005`

No valid stable path exists across the supplied topology.

### `MUD-006`

Calibration snapshot contains conflicting records for the same node.

### `MUD-007`

Cat lane noise exceeds the current shadow proposal envelope.

### `MUD-008`

Payload is harsh but bounded, redacted, and shadow-only.

## Boundary

Mud Run V0 is an adversarial local evidence harness. It does not submit backend jobs, validate physical quantum hardware, change pulses, authorize quarantine commands, or dispatch HAL actions.
