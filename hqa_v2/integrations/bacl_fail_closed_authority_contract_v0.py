"""BACL fail-closed authority contract for HQA V2.

This module captures a safety lesson from the storm lane: missing credentials
must never become a shortcut around the cryptographic boundary. If BACL signing
authority is absent, stale, revoked, malformed, or already consumed, the control
plane must fail closed.
"""

from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


HQA_V2_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = HQA_V2_ROOT / "logs" / "bacl_fail_closed_authority_contract_v0.json"
REPORT_PATH = HQA_V2_ROOT / "reports" / "HQA_BACL_FAIL_CLOSED_AUTHORITY_CONTRACT_V0.md"


@dataclass(frozen=True)
class AuthorityCase:
    name: str
    signer_present: bool
    public_key_registered: bool
    signature_valid: bool
    key_state: str
    requested_action: str


CASES = [
    AuthorityCase(
        name="valid_one_time_manifest",
        signer_present=True,
        public_key_registered=True,
        signature_valid=True,
        key_state="fresh",
        requested_action="SET:CRYO:PUMP:Q10 ON",
    ),
    AuthorityCase(
        name="missing_private_key",
        signer_present=False,
        public_key_registered=True,
        signature_valid=False,
        key_state="missing",
        requested_action="SET:CRYO:PUMP:Q10 ON",
    ),
    AuthorityCase(
        name="unregistered_public_key",
        signer_present=True,
        public_key_registered=False,
        signature_valid=True,
        key_state="unregistered",
        requested_action="SET:CRYO:PUMP:Q10 ON",
    ),
    AuthorityCase(
        name="malformed_signature",
        signer_present=True,
        public_key_registered=True,
        signature_valid=False,
        key_state="fresh",
        requested_action="SET:CRYO:PUMP:Q10 ON",
    ),
    AuthorityCase(
        name="lamport_key_reuse",
        signer_present=True,
        public_key_registered=True,
        signature_valid=True,
        key_state="already_used",
        requested_action="SET:CRYO:PUMP:Q10 ON",
    ),
    AuthorityCase(
        name="revoked_key",
        signer_present=True,
        public_key_registered=True,
        signature_valid=True,
        key_state="revoked",
        requested_action="SET:CRYO:PUMP:Q10 ON",
    ),
]


def evaluate_case(case: AuthorityCase) -> dict[str, Any]:
    if not case.signer_present:
        decision = "SAFE_HOLD"
        reason = "MISSING_SIGNER_FAIL_CLOSED"
    elif not case.public_key_registered:
        decision = "SKULL_LOCK"
        reason = "UNREGISTERED_PUBLIC_KEY"
    elif case.key_state == "revoked":
        decision = "SKULL_LOCK"
        reason = "KEY_REVOKED"
    elif case.key_state == "already_used":
        decision = "SKULL_LOCK"
        reason = "LAMPORT_ONE_TIME_KEY_REUSE"
    elif not case.signature_valid:
        decision = "SKULL_LOCK"
        reason = "SIGNATURE_INVALID"
    else:
        decision = "AUTHORIZED_DRY_RUN_ONLY"
        reason = "FRESH_SIGNED_MANIFEST"

    return {
        **asdict(case),
        "decision": decision,
        "reason": reason,
        "raw_fallback_allowed": False,
        "hardware_authority": False,
        "real_actuator_authority": False,
    }


def run_contract() -> dict[str, Any]:
    evaluations = [evaluate_case(case) for case in CASES]
    payload = {
        "schema_version": "hqa.bacl_fail_closed_authority_contract.v0",
        "execution_mode": "local_policy_replay",
        "cases": evaluations,
        "authorized_cases": [case["name"] for case in evaluations if case["decision"] == "AUTHORIZED_DRY_RUN_ONLY"],
        "blocked_cases": [case["name"] for case in evaluations if case["decision"] in {"SKULL_LOCK", "SAFE_HOLD"}],
        "raw_fallback_allowed": False,
        "hardware_authority": False,
        "real_actuator_authority": False,
        "policy_rule": "BACL absence or failure must fail closed. Missing credentials, invalid signatures, unregistered keys, revoked keys, and one-time-key reuse cannot fall back to raw pump activation.",
        "boundary": "This contract is a local authority-policy proof. It signs no live commands, opens no sockets, reads no external secrets, and grants no HAL or actuator authority.",
    }
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def write_report(payload: dict[str, Any]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# HQA BACL Fail-Closed Authority Contract V0",
        "",
        "## Purpose",
        "",
        "This contract formalizes a hard authority rule: BACL failure must never degrade into raw hardware command fallback.",
        "",
        "## Summary",
        "",
        f"- Execution mode: `{payload['execution_mode']}`",
        f"- Raw fallback allowed: `{payload['raw_fallback_allowed']}`",
        f"- Hardware authority: `{payload['hardware_authority']}`",
        f"- Real actuator authority: `{payload['real_actuator_authority']}`",
        "",
        "| Case | Decision | Reason | Raw Fallback Allowed |",
        "|---|---|---|---:|",
    ]
    for case in payload["cases"]:
        lines.append(
            f"| `{case['name']}` | `{case['decision']}` | `{case['reason']}` | `{case['raw_fallback_allowed']}` |"
        )

    lines.extend(
        [
            "",
            "## Policy Rule",
            "",
            payload["policy_rule"],
            "",
            "## Boundary",
            "",
            payload["boundary"],
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    payload = run_contract()
    write_report(payload)
    print(f"HQA BACL fail-closed authority contract written: {REPORT_PATH}")
    print(f"- authorized dry-run cases: {len(payload['authorized_cases'])}")
    print(f"- blocked cases: {len(payload['blocked_cases'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

