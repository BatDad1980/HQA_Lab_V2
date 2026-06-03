"""Quality gate for HQA Field Map Replay V0."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


HQA_V2_ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = HQA_V2_ROOT / "logs" / "field_map_replay_v0.json"
OUTPUT_ROOT = HQA_V2_ROOT / "outputs" / "field_map_replay_v0"
REPORT_PATH = HQA_V2_ROOT / "reports" / "HQA_FIELD_MAP_REPLAY_GATE.md"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def manifest_valid() -> tuple[bool, str]:
    manifest_path = OUTPUT_ROOT / "MANIFEST_SHA256.txt"
    if not manifest_path.exists():
        return False, "Manifest missing."
    failures = []
    for line in manifest_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        expected, filename = line.split(maxsplit=1)
        path = OUTPUT_ROOT / filename.strip()
        if not path.exists():
            failures.append(f"{filename} missing")
            continue
        if sha256(path) != expected:
            failures.append(f"{filename} hash mismatch")
    return (not failures, "; ".join(failures) if failures else "All artifact hashes match.")


def write_report(checks: list[tuple[str, bool, str]]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    passed = sum(1 for _, ok, _ in checks)
    lines = [
        "# HQA Field Map Replay Gate",
        "",
        "## Purpose",
        "",
        "This gate verifies that field-map evidence becomes bounded shadow review artifacts without execution authority.",
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
            "This gate validates shadow replay artifacts only. It does not validate live quantum performance, submit jobs, run circuits, alter routing tables, change pulses, or authorize HAL execution.",
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    if not INPUT_PATH.exists():
        checks = [("replay_exists", False, "Run field_map_replay_v0.py first.")]
        write_report(checks)
        print(f"HQA field map replay gate written: {REPORT_PATH}")
        return 1
    replay: dict[str, Any] = load_json(INPUT_PATH)
    manifest_ok, manifest_detail = manifest_valid()
    candidates = replay.get("ranked_quarantine_candidates", [])
    artifacts = [
        OUTPUT_ROOT / "01_quarantine_candidates.json",
        OUTPUT_ROOT / "02_reroute_review.json",
        OUTPUT_ROOT / "03_intervention_hint.json",
    ]
    artifact_payloads = [load_json(path) for path in artifacts if path.exists()]

    checks = [
        ("schema_version", replay.get("schema_version") == "hqa.field_map_replay.v0", "Replay schema is V0."),
        ("shadow_only", replay.get("execution_mode") == "shadow_replay_only", f"Mode: `{replay.get('execution_mode')}`."),
        ("no_hardware_authority", replay.get("hardware_authority") is False and all(payload.get("hardware_authority") is False for payload in artifact_payloads), "No artifact grants hardware authority."),
        ("no_jobs_submitted", replay.get("jobs_submitted") == 0, "Replay submitted zero jobs."),
        ("candidates_ranked", len(candidates) >= 3 and candidates[0]["risk_score"] >= candidates[-1]["risk_score"], f"Candidates: `{len(candidates)}`."),
        ("targets_selected", len(replay.get("recommended_targets", [])) >= 1, f"Targets: `{replay.get('recommended_targets')}`."),
        ("edge_neighborhoods_present", len(replay.get("avoided_edge_neighborhoods", [])) >= 1, "Damaged edge neighborhoods are represented."),
        ("review_required", replay.get("review_packet", {}).get("operator_review_required") is True, "Operator review required for non-nominal field."),
        ("intervention_bounded", replay.get("intervention_mode") in {"MONITOR_WITH_SHADOW_OPTIMIZATION", "QUARANTINE_REMAP_SHADOW", "NO_INTERVENTION"}, f"Mode: `{replay.get('intervention_mode')}`."),
        ("artifacts_present", all(path.exists() for path in artifacts), "All replay artifacts exist."),
        ("manifest_valid", manifest_ok, manifest_detail),
        ("boundary_present", "submits zero jobs" in replay.get("boundary", "") and "grants no HAL authority" in replay.get("boundary", ""), "Boundary blocks jobs and HAL authority."),
    ]

    write_report(checks)
    failed = [check for check in checks if not check[1]]
    print(f"HQA field map replay gate written: {REPORT_PATH}")
    print(f"Passed {len(checks) - len(failed)}/{len(checks)} checks.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
