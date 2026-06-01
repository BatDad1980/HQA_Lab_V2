"""Quality gate for the legacy autonomic stress regulator harvest."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


HQA_V2_ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = HQA_V2_ROOT / "logs" / "legacy_autonomic_stress_regulator_v0.json"
REPORT_PATH = HQA_V2_ROOT / "reports" / "HQA_LEGACY_AUTONOMIC_STRESS_REGULATOR_GATE.md"


def load_payload() -> dict[str, Any]:
    return json.loads(INPUT_PATH.read_text(encoding="utf-8"))


def write_report(checks: list[tuple[str, bool, str]]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    passed = sum(1 for _, ok, _ in checks if ok)
    lines = [
        "# HQA Legacy Autonomic Stress Regulator Gate",
        "",
        "## Purpose",
        "",
        "This gate verifies that the legacy autonomic stress harvest emits bounded patch-state decisions only.",
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
        status = "PASS" if ok else "FAIL"
        lines.append(f"| {name} | {status} | {detail} |")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This gate validates advisory stress classification only. It does not validate physical quantum hardware, production QEC performance, live backend access, pulse changes, or HAL execution.",
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    if not INPUT_PATH.exists():
        checks = [("input_exists", False, "Run legacy_autonomic_stress_regulator_v0.py first.")]
        write_report(checks)
        print(f"HQA legacy autonomic stress gate written: {REPORT_PATH}")
        return 1

    payload = load_payload()
    decisions = payload.get("decisions", [])
    by_patch = {item.get("patch_id"): item for item in decisions}
    disallowed = payload.get("disallowed_outputs", {})
    scores = [float(item.get("stress_score", -1.0)) for item in decisions]

    checks = [
        ("schema_version", payload.get("schema_version") == "hqa.legacy_autonomic_stress_regulator.v0", "Schema is V0."),
        ("shadow_advisory_mode", payload.get("execution_mode") == "shadow_advisory", f"Mode: `{payload.get('execution_mode')}`."),
        ("no_hardware_authority", payload.get("hardware_authority") is False, "No hardware authority present."),
        ("all_patches_present", set(by_patch) == {"PATCH_NW", "PATCH_NE", "PATCH_SW", "PATCH_SE"}, f"Patches: `{sorted(by_patch)}`."),
        ("scores_bounded", all(0.0 <= score <= 1.0 for score in scores), f"Scores: `{scores}`."),
        ("green_patch_monitors", by_patch.get("PATCH_NW", {}).get("advisory_action") == "MONITOR_ONLY", f"NW action: `{by_patch.get('PATCH_NW', {}).get('advisory_action')}`."),
        ("calibration_hold_present", by_patch.get("PATCH_NE", {}).get("advisory_action") == "PROPOSE_CALIBRATION_HOLD", f"NE action: `{by_patch.get('PATCH_NE', {}).get('advisory_action')}`."),
        ("reroute_review_present", by_patch.get("PATCH_SW", {}).get("advisory_action") == "PROPOSE_REROUTE_REVIEW", f"SW action: `{by_patch.get('PATCH_SW', {}).get('advisory_action')}`."),
        ("safe_hold_on_no_route", by_patch.get("PATCH_SE", {}).get("advisory_action") == "SAFE_HOLD", f"SE action: `{by_patch.get('PATCH_SE', {}).get('advisory_action')}`."),
        ("highest_stress_patch", payload.get("highest_stress_patch") == "PATCH_SE", f"Highest: `{payload.get('highest_stress_patch')}`."),
        ("no_disallowed_outputs", all(value == 0 for value in disallowed.values()), f"Disallowed outputs: `{disallowed}`."),
        ("boundary_present", "does not dispatch cooling" in payload.get("boundary", ""), "Boundary rejects live dispatch."),
    ]

    write_report(checks)
    failed = [check for check in checks if not check[1]]
    print(f"HQA legacy autonomic stress gate written: {REPORT_PATH}")
    print(f"Passed {len(checks) - len(failed)}/{len(checks)} checks.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
