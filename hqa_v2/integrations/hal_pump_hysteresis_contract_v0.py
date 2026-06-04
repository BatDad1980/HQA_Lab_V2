"""HAL pump hysteresis contract for HQA V2.

This module captures the storm-lane regression where a stress response turned a
mock cryostat pump on and the stabilization rule turned it back off in the same
control tick. The clean contract requires a hold window: activation and
deactivation cannot collapse into one cycle.
"""

from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


HQA_V2_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = HQA_V2_ROOT / "logs" / "hal_pump_hysteresis_contract_v0.json"
REPORT_PATH = HQA_V2_ROOT / "reports" / "HQA_HAL_PUMP_HYSTERESIS_CONTRACT_V0.md"


@dataclass(frozen=True)
class PumpTick:
    name: str
    stress_active: bool
    temperature_mk: float
    pump_previously_active: bool
    ticks_since_activation: int | None


MIN_HOLD_TICKS = 1


CASES = [
    PumpTick(
        name="stress_at_stable_temperature",
        stress_active=True,
        temperature_mk=10.0,
        pump_previously_active=False,
        ticks_since_activation=None,
    ),
    PumpTick(
        name="new_activation_same_tick_stabilization_attempt",
        stress_active=True,
        temperature_mk=9.8,
        pump_previously_active=False,
        ticks_since_activation=None,
    ),
    PumpTick(
        name="active_pump_first_hold_tick",
        stress_active=False,
        temperature_mk=9.8,
        pump_previously_active=True,
        ticks_since_activation=0,
    ),
    PumpTick(
        name="active_pump_after_hold_window",
        stress_active=False,
        temperature_mk=9.8,
        pump_previously_active=True,
        ticks_since_activation=2,
    ),
    PumpTick(
        name="high_temperature_no_prior_pump",
        stress_active=False,
        temperature_mk=17.5,
        pump_previously_active=False,
        ticks_since_activation=None,
    ),
]


def evaluate_tick(tick: PumpTick) -> dict[str, Any]:
    activated_this_tick = bool(tick.stress_active or tick.temperature_mk > 15.0) and not tick.pump_previously_active
    if activated_this_tick:
        decision = "PUMP_ON_HOLD"
        reason = "ACTIVATION_HOLDS_FOR_MINIMUM_WINDOW"
    elif tick.pump_previously_active and tick.temperature_mk <= 10.0:
        if tick.ticks_since_activation is not None and tick.ticks_since_activation >= MIN_HOLD_TICKS:
            decision = "PUMP_OFF_ALLOWED"
            reason = "STABILIZED_AFTER_HOLD_WINDOW"
        else:
            decision = "PUMP_ON_HOLD"
            reason = "STABILIZED_BUT_HOLD_WINDOW_ACTIVE"
    elif tick.pump_previously_active:
        decision = "PUMP_ON"
        reason = "PUMP_ALREADY_ACTIVE_AND_NOT_STABILIZED"
    else:
        decision = "PUMP_OFF"
        reason = "NO_STRESS_AND_NO_HIGH_TEMPERATURE"

    return {
        **asdict(tick),
        "activated_this_tick": activated_this_tick,
        "decision": decision,
        "reason": reason,
        "same_tick_activation_deactivation_allowed": False,
        "hardware_authority": False,
        "real_actuator_authority": False,
    }


def run_contract() -> dict[str, Any]:
    evaluations = [evaluate_tick(case) for case in CASES]
    payload = {
        "schema_version": "hqa.hal_pump_hysteresis_contract.v0",
        "execution_mode": "local_control_policy_replay",
        "min_hold_ticks": MIN_HOLD_TICKS,
        "cases": evaluations,
        "same_tick_activation_deactivation_allowed": False,
        "hardware_authority": False,
        "real_actuator_authority": False,
        "policy_rule": "A pump activated by stress or high temperature must hold for at least one control tick before stabilization logic may deactivate it.",
        "boundary": "This contract models pump-state policy only. It opens no sockets, sends no SCPI commands, activates no pumps, and grants no HAL or actuator authority.",
    }
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def write_report(payload: dict[str, Any]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# HQA HAL Pump Hysteresis Contract V0",
        "",
        "## Purpose",
        "",
        "This contract prevents a same-cycle contradiction in the autonomic cooling loop: a stress response cannot activate a pump and then immediately deactivate it in the same tick because the pre-action temperature was already stable.",
        "",
        "## Summary",
        "",
        f"- Execution mode: `{payload['execution_mode']}`",
        f"- Minimum hold ticks: `{payload['min_hold_ticks']}`",
        f"- Same-tick activation/deactivation allowed: `{payload['same_tick_activation_deactivation_allowed']}`",
        f"- Hardware authority: `{payload['hardware_authority']}`",
        f"- Real actuator authority: `{payload['real_actuator_authority']}`",
        "",
        "| Case | Decision | Reason |",
        "|---|---|---|",
    ]
    for case in payload["cases"]:
        lines.append(f"| `{case['name']}` | `{case['decision']}` | `{case['reason']}` |")

    lines.extend(
        [
            "",
            "## Policy Rule",
            "",
            payload["policy_rule"],
            "",
            "## Boundary",
            "",
            payload["boundary"],
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    payload = run_contract()
    write_report(payload)
    print(f"HQA HAL pump hysteresis contract written: {REPORT_PATH}")
    print(f"- cases: {len(payload['cases'])}")
    print(f"- same-tick activation/deactivation allowed: {payload['same_tick_activation_deactivation_allowed']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

