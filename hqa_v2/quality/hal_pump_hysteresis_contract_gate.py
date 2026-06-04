"""Quality gate for HAL pump hysteresis contract V0."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


HQA_V2_ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = HQA_V2_ROOT / "logs" / "hal_pump_hysteresis_contract_v0.json"
REPORT_PATH = HQA_V2_ROOT / "reports" / "HQA_HAL_PUMP_HYSTERESIS_CONTRACT_GATE.md"


def write_report(checks: list[tuple[str, bool, str]]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    passed = sum(1 for _, ok, _ in checks)
    lines = [
        "# HQA HAL Pump Hysteresis Contract Gate",
        "",
        "## Purpose",
        "",
        "This gate verifies that autonomic pump activation cannot be undone by stabilization logic in the same control tick.",
        "",
        "## Results",
        "",
        f"- Checks: `{len(checks)}`",
        f"- Passed: `{passed}`",
        f"- Failed: `{len(checks) - passed}`",
        "",
        "| Check | Status | Detail |",
        "|---|---:|---|",
    ]
    for name, ok, detail in checks:
        lines.append(f"| {name} | {'PASS' if ok else 'FAIL'} | {detail} |")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This gate validates local pump-state policy only. It does not send SCPI commands, open sockets, activate pumps, or authorize HAL execution.",
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    if not INPUT_PATH.exists():
        checks = [("contract_output_exists", False, "Run hal_pump_hysteresis_contract_v0.py first.")]
        write_report(checks)
        print(f"HQA HAL pump hysteresis contract gate written: {REPORT_PATH}")
        return 1

    payload: dict[str, Any] = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
    cases = {case.get("name"): case for case in payload.get("cases", [])}

    checks = [
        ("schema_version", payload.get("schema_version") == "hqa.hal_pump_hysteresis_contract.v0", "Contract schema is V0."),
        ("local_control_policy_replay", payload.get("execution_mode") == "local_control_policy_replay", f"Mode: `{payload.get('execution_mode')}`."),
        ("same_tick_deactivation_blocked", payload.get("same_tick_activation_deactivation_allowed") is False, "Same-tick activation/deactivation is blocked."),
        ("no_hardware_authority", payload.get("hardware_authority") is False, "No hardware authority granted."),
        ("no_real_actuator_authority", payload.get("real_actuator_authority") is False, "No real actuator authority granted."),
        ("stress_at_stable_temp_holds", cases.get("stress_at_stable_temperature", {}).get("decision") == "PUMP_ON_HOLD", "Stress response holds even at stable temperature."),
        ("same_tick_stabilization_holds", cases.get("new_activation_same_tick_stabilization_attempt", {}).get("decision") == "PUMP_ON_HOLD", "Same-tick stabilization cannot undo new activation."),
        ("first_hold_tick_holds", cases.get("active_pump_first_hold_tick", {}).get("decision") == "PUMP_ON_HOLD", "First hold tick keeps pump active."),
        ("after_hold_deactivation_allowed", cases.get("active_pump_after_hold_window", {}).get("decision") == "PUMP_OFF_ALLOWED", "Deactivation is allowed after hold window."),
        ("high_temperature_activates_hold", cases.get("high_temperature_no_prior_pump", {}).get("decision") == "PUMP_ON_HOLD", "High temperature activation enters hold."),
        ("policy_rule_mentions_hold", "at least one control tick" in payload.get("policy_rule", ""), "Policy rule declares minimum hold window."),
        ("boundary_blocks_actuation", "opens no sockets" in payload.get("boundary", "") and "activates no pumps" in payload.get("boundary", ""), "Boundary blocks sockets and pump activation."),
    ]

    write_report(checks)
    failed = [check for check in checks if not check[1]]
    print(f"HQA HAL pump hysteresis contract gate written: {REPORT_PATH}")
    print(f"Passed {len(checks) - len(failed)}/{len(checks)} checks.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())

