"""Quality gate for Shadow Adaptive Proposal V0."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


HQA_V2_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_ROOT = HQA_V2_ROOT / "outputs" / "shadow_adaptive_proposal_v0"
REPORT_PATH = HQA_V2_ROOT / "reports" / "HQA_SHADOW_ADAPTIVE_PROPOSAL_GATE.md"


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
        expected, filename = line.split(maxsplit=1)
        path = OUTPUT_ROOT / filename.strip()
        if not path.exists():
            failures.append(f"{filename} missing")
            continue
        actual = sha256(path)
        if actual != expected:
            failures.append(f"{filename} hash mismatch")
    if failures:
        return False, "; ".join(failures)
    return True, "All artifact hashes match."


def write_report(checks: list[tuple[str, bool, str]]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    passed = sum(1 for _, ok, _ in checks if ok)
    lines = [
        "# HQA Shadow Adaptive Proposal Gate",
        "",
        "## Purpose",
        "",
        "This gate verifies that Shadow Adaptive Proposal V0 emits reviewable artifacts without live authority.",
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
            "This gate checks shadow-review packet structure only. It does not validate physical quantum hardware, production QEC performance, or live HAL execution.",
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    quarantine_path = OUTPUT_ROOT / "01_quarantine_decision.json"
    reroute_path = OUTPUT_ROOT / "02_reroute_review.json"
    hal_path = OUTPUT_ROOT / "03_hal_dry_run_manifest.json"

    missing = [path.name for path in [quarantine_path, reroute_path, hal_path] if not path.exists()]
    if missing:
        checks = [("artifacts_present", False, f"Missing: `{missing}`")]
        write_report(checks)
        print(f"HQA shadow adaptive proposal gate written: {REPORT_PATH}")
        return 1

    quarantine = load_json(quarantine_path)
    reroute = load_json(reroute_path)
    hal = load_json(hal_path)
    manifest_ok, manifest_detail = manifest_valid()

    checks = [
        ("quarantine_schema", quarantine.get("schema_version") == "hqa.quarantine_decision.v1", "Quarantine payload uses vendor schema."),
        ("quarantine_shadow_only", quarantine.get("authority") == "shadow_advisory", f"Authority: `{quarantine.get('authority')}`."),
        ("quarantine_target_q1", quarantine.get("target_id") == "Q_1", f"Target: `{quarantine.get('target_id')}`."),
        ("reroute_shadow_only", reroute.get("execution_mode") == "shadow_advisory", f"Mode: `{reroute.get('execution_mode')}`."),
        ("reroute_requires_review", reroute.get("requires_vendor_review") is True, "Vendor review is required."),
        ("reroute_avoids_q1", "Q_1" in reroute.get("avoided_targets", []), f"Avoided targets: `{reroute.get('avoided_targets')}`."),
        ("hal_schema", hal.get("schema_version") == "hqa.hal_manifest.v1", "HAL payload uses vendor schema."),
        ("hal_dry_run_only", hal.get("execution_mode") == "dry_run", f"Mode: `{hal.get('execution_mode')}`."),
        ("hal_requires_human_approval", hal.get("requires_human_approval") is True, "Human approval is required."),
        ("manifest_valid", manifest_ok, manifest_detail),
    ]

    write_report(checks)
    failed = [check for check in checks if not check[1]]
    print(f"HQA shadow adaptive proposal gate written: {REPORT_PATH}")
    print(f"Passed {len(checks) - len(failed)}/{len(checks)} checks.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
