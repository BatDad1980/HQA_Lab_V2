"""Quality gate for HQA Simulator Stress Schedule V0."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


HQA_V2_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_ROOT = HQA_V2_ROOT / "outputs" / "simulator_stress_schedule_v0"
SUMMARY_PATH = OUTPUT_ROOT / "schedule_summary.json"
REPORT_PATH = HQA_V2_ROOT / "reports" / "HQA_SIMULATOR_STRESS_SCHEDULE_GATE.md"

EXPECTED_ACTIONS = {
    "nominal": "MONITOR_ONLY",
    "mild_stress": "MONITOR_WITH_ROUTE_REVIEW",
    "correlated_stress": "ROUTE_REVIEW_AND_QUARANTINE_PROPOSAL",
    "no_route_hold": "NO_ROUTE_HOLD_REVIEW",
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def manifest_valid() -> tuple[bool, str]:
    manifest_path = OUTPUT_ROOT / "MANIFEST_SHA256.txt"
    if not manifest_path.exists():
        return False, "Manifest missing."
    failures: list[str] = []
    for line in manifest_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        expected, relative = line.split(maxsplit=1)
        path = OUTPUT_ROOT / relative.strip()
        if not path.exists():
            failures.append(f"{relative} missing")
            continue
        if sha256(path) != expected:
            failures.append(f"{relative} hash mismatch")
    if failures:
        return False, "; ".join(failures)
    return True, "All schedule artifact hashes match."


def write_report(checks: list[tuple[str, bool, str]]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    passed = sum(1 for _, ok, _ in checks if ok)
    lines = [
        "# HQA Simulator Stress Schedule Gate",
        "",
        "## Purpose",
        "",
        "This gate verifies that Simulator Stress Schedule V0 produces bounded advisory outputs across multiple local stress profiles.",
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
            "This gate checks deterministic local schedule behavior only. It does not validate physical quantum hardware, production QEC performance, or live HAL execution.",
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    if not SUMMARY_PATH.exists():
        checks = [("summary_exists", False, f"Missing `{SUMMARY_PATH}`")]
        write_report(checks)
        print(f"HQA simulator stress schedule gate written: {REPORT_PATH}")
        return 1

    summary = load_json(SUMMARY_PATH)
    results = {item["scenario"]: item for item in summary.get("results", [])}
    manifest_ok, manifest_detail = manifest_valid()
    ordered_scores = [
        float(results.get(name, {}).get("top_risk_score", -1.0))
        for name in ["nominal", "mild_stress", "correlated_stress", "no_route_hold"]
    ]
    actions_match = all(results.get(name, {}).get("advisory_action") == action for name, action in EXPECTED_ACTIONS.items())
    no_authority = all(item.get("hardware_authority") is False for item in results.values())
    scenario_dirs_exist = all((OUTPUT_ROOT / name).exists() for name in EXPECTED_ACTIONS)

    checks = [
        ("schema_version", summary.get("schema_version") == "hqa.simulator_stress_schedule.v0", "Schedule summary schema is V0."),
        ("four_scenarios_present", set(results) == set(EXPECTED_ACTIONS), f"Scenarios found: `{sorted(results)}`."),
        ("scenario_dirs_exist", scenario_dirs_exist, "All scenario evidence folders exist."),
        ("actions_match_profiles", actions_match, f"Actions: `{ {name: results.get(name, {}).get('advisory_action') for name in EXPECTED_ACTIONS} }`."),
        ("risk_scores_bounded", all(0.0 <= score <= 1.0 for score in ordered_scores), f"Scores: `{ordered_scores}`."),
        ("risk_increases_with_stress", ordered_scores == sorted(ordered_scores), f"Ordered scores: `{ordered_scores}`."),
        ("no_hardware_authority", no_authority, "No schedule result grants hardware authority."),
        ("no_route_hold_blocks_proposal", results.get("no_route_hold", {}).get("proposal_mode") == "blocked", f"Mode: `{results.get('no_route_hold', {}).get('proposal_mode')}`."),
        ("nominal_monitor_only", results.get("nominal", {}).get("advisory_action") == "MONITOR_ONLY", "Nominal profile remains monitor-only."),
        ("manifest_valid", manifest_ok, manifest_detail),
    ]

    write_report(checks)
    failed = [check for check in checks if not check[1]]
    print(f"HQA simulator stress schedule gate written: {REPORT_PATH}")
    print(f"Passed {len(checks) - len(failed)}/{len(checks)} checks.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
