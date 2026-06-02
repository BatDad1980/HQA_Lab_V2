"""Quality gate for HQA Mud Run V0."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


HQA_V2_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_ROOT = HQA_V2_ROOT / "outputs" / "hqa_mud_run_v0"
SUMMARY_PATH = OUTPUT_ROOT / "mud_run_summary.json"
REPORT_PATH = HQA_V2_ROOT / "reports" / "HQA_MUD_RUN_GATE.md"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def manifest_valid() -> tuple[bool, str]:
    manifest = OUTPUT_ROOT / "MANIFEST_SHA256.txt"
    if not manifest.exists():
        return False, "Manifest missing."
    failures: list[str] = []
    for line in manifest.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        expected, relative = line.split(maxsplit=1)
        path = OUTPUT_ROOT / relative.strip()
        if not path.exists():
            failures.append(f"{relative} missing")
        elif sha256(path) != expected:
            failures.append(f"{relative} hash mismatch")
    return (not failures, "All mud-run hashes match." if not failures else "; ".join(failures))


def write_report(checks: list[tuple[str, bool, str]]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    passed = sum(1 for _, ok, _ in checks if ok)
    lines = [
        "# HQA Mud Run Gate",
        "",
        "## Purpose",
        "",
        "This gate verifies that Mud Run V0 reaches the expected fail-closed breakpoints.",
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
            "This gate validates local adversarial intake behavior only. It does not validate physical quantum hardware, production QEC performance, live backend access, pulse changes, or HAL execution.",
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    if not SUMMARY_PATH.exists():
        checks = [("summary_exists", False, f"Missing `{SUMMARY_PATH}`.")]
        write_report(checks)
        print(f"HQA mud run gate written: {REPORT_PATH}")
        return 1

    payload = load_json(SUMMARY_PATH)
    results = {item["scenario_id"]: item for item in payload.get("results", [])}
    expected = {item["scenario_id"]: item for item in payload.get("expected", [])}
    manifest_ok, manifest_detail = manifest_valid()
    dispositions = {item.get("disposition") for item in results.values()}
    breakpoints = {item.get("breakpoint") for item in results.values()}

    expected_match = all(
        results.get(sid, {}).get("disposition") == item["expected_disposition"]
        and results.get(sid, {}).get("breakpoint") == item["expected_breakpoint"]
        for sid, item in expected.items()
    )
    no_authority = all(item.get("hardware_authority") is False for item in results.values())
    has_fail_closed = {"REJECT", "QUARANTINE", "REVIEW_LOCK", "SAFE_HOLD"} <= dispositions

    checks = [
        ("schema_version", payload.get("schema_version") == "hqa.mud_run.v0", "Mud-run schema is V0."),
        ("adversarial_shadow_mode", payload.get("execution_mode") == "adversarial_shadow_harness", f"Mode: `{payload.get('execution_mode')}`."),
        ("no_hardware_authority", payload.get("hardware_authority") is False and no_authority, "No mud-run result grants hardware authority."),
        ("eight_scenarios", len(results) == 8 and len(expected) == 8, f"Results `{len(results)}`, expected `{len(expected)}`."),
        ("expected_breakpoints_match", expected_match, "Every scenario reached its expected disposition and breakpoint."),
        ("fail_closed_modes_present", has_fail_closed, f"Dispositions: `{sorted(dispositions)}`."),
        ("accept_shadow_still_possible", "ACCEPT_SHADOW" in dispositions, "A harsh but bounded payload can still enter shadow evaluation."),
        ("breakpoint_variety", len(breakpoints) >= 7, f"Breakpoints: `{sorted(breakpoints)}`."),
        ("manifest_valid", manifest_ok, manifest_detail),
        ("boundary_present", "no live hardware authority" in payload.get("boundary", "").lower(), "Boundary rejects live authority."),
    ]

    write_report(checks)
    failed = [check for check in checks if not check[1]]
    print(f"HQA mud run gate written: {REPORT_PATH}")
    print(f"Passed {len(checks) - len(failed)}/{len(checks)} checks.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
