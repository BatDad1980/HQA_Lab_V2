"""Quality gate for BACL fail-closed authority contract V0."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


HQA_V2_ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = HQA_V2_ROOT / "logs" / "bacl_fail_closed_authority_contract_v0.json"
REPORT_PATH = HQA_V2_ROOT / "reports" / "HQA_BACL_FAIL_CLOSED_AUTHORITY_CONTRACT_GATE.md"


def write_report(checks: list[tuple[str, bool, str]]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    passed = sum(1 for _, ok, _ in checks)
    lines = [
        "# HQA BACL Fail-Closed Authority Contract Gate",
        "",
        "## Purpose",
        "",
        "This gate verifies that BACL authority failures are locked or held instead of falling back to raw command execution.",
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
            "This gate validates local policy only. It does not sign live commands, open sockets, read external secrets, or authorize HAL execution.",
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    if not INPUT_PATH.exists():
        checks = [("contract_output_exists", False, "Run bacl_fail_closed_authority_contract_v0.py first.")]
        write_report(checks)
        print(f"HQA BACL fail-closed authority contract gate written: {REPORT_PATH}")
        return 1

    payload: dict[str, Any] = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
    cases = {case.get("name"): case for case in payload.get("cases", [])}
    blocked_decisions = {"SKULL_LOCK", "SAFE_HOLD"}

    checks = [
        ("schema_version", payload.get("schema_version") == "hqa.bacl_fail_closed_authority_contract.v0", "Contract schema is V0."),
        ("local_policy_replay", payload.get("execution_mode") == "local_policy_replay", f"Mode: `{payload.get('execution_mode')}`."),
        ("raw_fallback_globally_blocked", payload.get("raw_fallback_allowed") is False, "Global raw fallback is blocked."),
        ("no_hardware_authority", payload.get("hardware_authority") is False, "No hardware authority granted."),
        ("no_real_actuator_authority", payload.get("real_actuator_authority") is False, "No real actuator authority granted."),
        ("valid_manifest_dry_run_only", cases.get("valid_one_time_manifest", {}).get("decision") == "AUTHORIZED_DRY_RUN_ONLY", "Only fresh signed manifest gets dry-run authorization."),
        ("missing_key_safe_hold", cases.get("missing_private_key", {}).get("decision") == "SAFE_HOLD", "Missing signer fails closed."),
        ("unregistered_key_locked", cases.get("unregistered_public_key", {}).get("decision") == "SKULL_LOCK", "Unregistered key is locked."),
        ("malformed_signature_locked", cases.get("malformed_signature", {}).get("decision") == "SKULL_LOCK", "Malformed signature is locked."),
        ("key_reuse_locked", cases.get("lamport_key_reuse", {}).get("decision") == "SKULL_LOCK", "Lamport key reuse is locked."),
        ("revoked_key_locked", cases.get("revoked_key", {}).get("decision") == "SKULL_LOCK", "Revoked key is locked."),
        ("no_case_allows_raw_fallback", all(case.get("raw_fallback_allowed") is False for case in cases.values()), "No case allows raw fallback."),
        ("all_failure_cases_blocked", all(case.get("decision") in blocked_decisions for name, case in cases.items() if name != "valid_one_time_manifest"), "All authority failures are blocked."),
        ("policy_rule_present", "cannot fall back to raw pump activation" in payload.get("policy_rule", ""), "Policy rule blocks raw pump fallback."),
        ("boundary_blocks_live_authority", "signs no live commands" in payload.get("boundary", "") and "grants no HAL" in payload.get("boundary", ""), "Boundary blocks live commands and HAL authority."),
    ]

    write_report(checks)
    failed = [check for check in checks if not check[1]]
    print(f"HQA BACL fail-closed authority contract gate written: {REPORT_PATH}")
    print(f"Passed {len(checks) - len(failed)}/{len(checks)} checks.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())

