"""Quality gate for IBM live-validation abstention replay V0."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


HQA_V2_ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = HQA_V2_ROOT / "logs" / "ibm_live_validation_abstention_replay_v0.json"
REPORT_PATH = HQA_V2_ROOT / "reports" / "HQA_IBM_LIVE_VALIDATION_ABSTENTION_REPLAY_GATE.md"


def write_report(checks: list[tuple[str, bool, str]]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    passed = sum(1 for _, ok, _ in checks)
    lines = [
        "# HQA IBM Live Validation Abstention Replay Gate",
        "",
        "## Purpose",
        "",
        "This gate verifies that reported IBM validation outcomes are translated into bounded intervention policy without turning into a live authority claim.",
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
            "This gate validates policy replay only. It does not validate production QEC performance, submit IBM jobs, execute circuits, alter hardware routing, or authorize HAL execution.",
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    if not INPUT_PATH.exists():
        checks = [("replay_output_exists", False, "Run ibm_live_validation_abstention_replay_v0.py first.")]
        write_report(checks)
        print(f"HQA IBM live validation abstention replay gate written: {REPORT_PATH}")
        return 1

    payload: dict[str, Any] = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
    decisions = {item.get("backend"): item for item in payload.get("decisions", [])}
    fixtures = {item.get("backend"): item for item in payload.get("fixtures", [])}
    fez = decisions.get("ibm_fez", {})
    kingston = decisions.get("ibm_kingston", {})

    checks = [
        ("schema_version", payload.get("schema_version") == "hqa.ibm_live_validation_abstention_replay.v0", "Replay schema is V0."),
        ("reported_fixture_mode", payload.get("execution_mode") == "reported_fixture_policy_replay", f"Mode: `{payload.get('execution_mode')}`."),
        ("adjacent_source_labeled", payload.get("source_class") == "adjacent_lane_reported_live_validation", "Source is labeled as adjacent-lane report, not clean-lane proof."),
        ("no_clean_lane_jobs", payload.get("clean_lane_jobs_submitted") == 0, "Clean lane submitted zero IBM jobs."),
        ("no_hardware_authority", payload.get("hardware_authority") is False and all(item.get("hardware_authority") is False for item in decisions.values()), "No decision grants hardware authority."),
        ("both_backends_present", {"ibm_fez", "ibm_kingston"}.issubset(decisions) and {"ibm_fez", "ibm_kingston"}.issubset(fixtures), "Fez and Kingston are both replayed."),
        ("fez_positive_delta", float(fez.get("fidelity_delta", 0.0)) > 0.0, "Fez fixture shows quarantine-remap improvement."),
        ("fez_intervenes", fez.get("policy_decision") == "INTERVENE_WITH_QUARANTINE_REMAP_SHADOW", f"Fez decision: `{fez.get('policy_decision')}`."),
        ("kingston_negative_delta", float(kingston.get("fidelity_delta", 0.0)) < 0.0, "Kingston fixture shows forced-remap underperformance."),
        ("kingston_abstains", kingston.get("policy_decision") == "ABSTAIN_AND_MONITOR", f"Kingston decision: `{kingston.get('policy_decision')}`."),
        ("core_rule_condition_aware", "intervene only when measured field conditions justify it" in payload.get("core_rule", ""), "Core rule encodes condition-aware intervention."),
        ("boundary_blocks_overclaim", "does not submit IBM jobs" in payload.get("boundary", "") and "claim production quantum performance" in payload.get("boundary", ""), "Boundary blocks live-job and production-performance claims."),
    ]

    write_report(checks)
    failed = [check for check in checks if not check[1]]
    print(f"HQA IBM live validation abstention replay gate written: {REPORT_PATH}")
    print(f"Passed {len(checks) - len(failed)}/{len(checks)} checks.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())

