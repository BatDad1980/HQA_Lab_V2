"""Quality gate for HQA Intervention Gate V0."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


HQA_V2_ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = HQA_V2_ROOT / "logs" / "hqa_intervention_gate_v0.json"
REPORT_PATH = HQA_V2_ROOT / "reports" / "HQA_INTERVENTION_GATE_QUALITY.md"


def load_payload() -> dict[str, Any]:
    return json.loads(INPUT_PATH.read_text(encoding="utf-8"))


def write_report(checks: list[tuple[str, bool, str]]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    passed = sum(1 for _, ok, _ in checks if ok)
    lines = [
        "# HQA Intervention Gate Quality",
        "",
        "## Purpose",
        "",
        "This gate verifies that Intervention Gate V0 maps stress-run breakpoints to bounded policy decisions.",
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
            "This gate validates shadow policy decisions only. It does not validate physical quantum hardware, production QEC performance, live backend access, pulse changes, or HAL execution.",
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    if not INPUT_PATH.exists():
        checks = [("input_exists", False, "Run hqa_intervention_gate_v0.py first.")]
        write_report(checks)
        print(f"HQA intervention gate quality written: {REPORT_PATH}")
        return 1

    payload = load_payload()
    results = {item["scenario_id"]: item for item in payload.get("results", [])}
    expected = {item["scenario_id"]: item for item in payload.get("expected", [])}
    decisions = {item.get("decision") for item in results.values()}
    breakpoints = {item.get("breakpoint") for item in results.values()}
    no_authority = payload.get("hardware_authority") is False and all(item.get("hardware_authority") is False for item in results.values())
    expected_match = all(
        results.get(sid, {}).get("decision") == item["expected_decision"]
        and results.get(sid, {}).get("breakpoint") == item["expected_breakpoint"]
        for sid, item in expected.items()
    )

    checks = [
        ("schema_version", payload.get("schema_version") == "hqa.intervention_gate.v0", "Schema is V0."),
        ("shadow_policy_mode", payload.get("execution_mode") == "shadow_policy_gate", f"Mode: `{payload.get('execution_mode')}`."),
        ("no_hardware_authority", no_authority, "No intervention result grants hardware authority."),
        ("ten_scenarios", len(results) == 10 and len(expected) == 10, f"Results `{len(results)}`, expected `{len(expected)}`."),
        ("expected_results_match", expected_match, "Every scenario reached the expected decision and breakpoint."),
        ("stand_down_present", results.get("INT-001", {}).get("decision") == "NO_INTERVENTION", "Stable IBM rerun stands down."),
        ("shadow_remap_present", results.get("INT-002", {}).get("decision") == "SHADOW_REMAP_CANDIDATE", "Noisy IBM style remains shadow remap candidate."),
        ("patch_routing_required", "PATCH_ROUTING_REQUIRED" in decisions, f"Decisions: `{sorted(decisions)}`."),
        ("hard_block_present", "HARD_BLOCK" in decisions, "BACL exhausted key hard-blocks."),
        ("compression_required", "REQUIRE_SUMMARY_COMPRESSION" in decisions, "Cognitive overload requires compression."),
        ("safe_hold_breakpoints", {"latency_over_budget", "physics_error_proxy_exceeds_one"} <= breakpoints, f"Breakpoints: `{sorted(breakpoints)}`."),
        ("boundary_present", "does not authorize live hardware control" in payload.get("boundary", ""), "Boundary rejects live authority."),
    ]

    write_report(checks)
    failed = [check for check in checks if not check[1]]
    print(f"HQA intervention gate quality written: {REPORT_PATH}")
    print(f"Passed {len(checks) - len(failed)}/{len(checks)} checks.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
