"""Quality gate for HQA BACL Entropy Policy V0."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


HQA_V2_ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = HQA_V2_ROOT / "logs" / "bacl_entropy_policy_v0.json"
REPORT_PATH = HQA_V2_ROOT / "reports" / "HQA_BACL_ENTROPY_POLICY_GATE.md"


def write_report(checks: list[tuple[str, bool, str]]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    passed = sum(1 for _, ok, _ in checks)
    lines = [
        "# HQA BACL Entropy Policy Gate",
        "",
        "## Purpose",
        "",
        "This gate verifies that the BACL entropy policy identifies public-only deterministic seeding as unsafe and blocks telemetry-only forgery under the hardened scheme.",
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
            "This gate validates local entropy policy only. It does not validate production cryptography, sign live commands, submit jobs, alter pulses, or authorize HAL execution.",
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    if not INPUT_PATH.exists():
        checks = [("policy_output_exists", False, "Run bacl_entropy_policy_v0.py first.")]
        write_report(checks)
        print(f"HQA BACL entropy policy gate written: {REPORT_PATH}")
        return 1

    payload: dict[str, Any] = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
    legacy = payload.get("legacy_public_seed_demo", {})
    hardened = payload.get("hardened_hkdf_salt_demo", {})
    checks_payload = payload.get("policy_checks", {})

    checks = [
        ("schema_version", payload.get("schema_version") == "hqa.bacl_entropy_policy.v0", "Policy schema is V0."),
        ("local_policy_proof", payload.get("execution_mode") == "local_policy_proof", f"Mode: `{payload.get('execution_mode')}`."),
        ("legacy_attack_reproduced", legacy.get("attacker_key_matched") is True and legacy.get("forged_manifest_decision") == "AUTHORIZED", "Legacy public-only seed reproduces signing key."),
        ("hardened_key_diverges", hardened.get("attacker_key_matched") is False, "Attacker without private salt cannot reproduce key."),
        ("hardened_forgery_locked", hardened.get("forged_manifest_decision") == "SKULL_LOCK", "Hardened forged manifest is locked."),
        ("private_salt_required", hardened.get("private_salt_required") is True and checks_payload.get("private_salt_required") is True, "Private salt is required."),
        ("public_only_seed_rejected_rule", "public telemetry alone" in payload.get("decision_rule", ""), "Decision rule rejects telemetry-only signing authority."),
        ("no_live_command_signed", checks_payload.get("live_command_signed") is False, "No live command signed."),
        ("no_hardware_authority", payload.get("hardware_authority") is False and checks_payload.get("hardware_authority") is False, "No hardware authority granted."),
        ("no_jobs_submitted", payload.get("jobs_submitted") == 0, "Zero provider jobs submitted."),
        ("boundary_present", "reads no external secrets" in payload.get("boundary", "") and "grants no HAL authority" in payload.get("boundary", ""), "Boundary blocks external secrets and HAL authority."),
    ]

    write_report(checks)
    failed = [check for check in checks if not check[1]]
    print(f"HQA BACL entropy policy gate written: {REPORT_PATH}")
    print(f"Passed {len(checks) - len(failed)}/{len(checks)} checks.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
