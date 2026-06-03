"""BACL entropy policy demo for HQA V2.

This module captures the red-team lesson from the legacy deterministic seeding
failure: public telemetry must never be sufficient to derive signing authority.

It is a local policy proof only. It does not sign live commands, control
hardware, read external secrets, or replace production cryptography.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


HQA_V2_ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = HQA_V2_ROOT / "logs" / "bacl_entropy_policy_v0.json"
REPORT_PATH = HQA_V2_ROOT / "reports" / "HQA_BACL_ENTROPY_POLICY_V0.md"


LEGACY_PUBLIC_SEED = "environment:earth,mass:0.0,velocity:(0.0,0.0)"
PRIVATE_SYSTEM_SALT = "HQA_LOCAL_TEST_SALT_NOT_A_REAL_SECRET"
ATTACKER_WRONG_SALT = ""


@dataclass(frozen=True)
class SignedManifest:
    manifest_id: str
    payload: dict[str, Any]
    key_fingerprint: str
    signature: str


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def legacy_key(public_seed: str) -> str:
    return digest(f"legacy-public-seed::{public_seed}")


def hkdf_like_key(public_seed: str, private_salt: str) -> str:
    # Local policy proof: HMAC captures the required private-salt property.
    return hmac.new(private_salt.encode("utf-8"), public_seed.encode("utf-8"), hashlib.sha256).hexdigest()


def fingerprint(key: str) -> str:
    return digest(f"fingerprint::{key}")[:16]


def sign_manifest(manifest_id: str, payload: dict[str, Any], key: str) -> SignedManifest:
    body = json.dumps({"manifest_id": manifest_id, "payload": payload}, sort_keys=True)
    signature = hmac.new(key.encode("utf-8"), body.encode("utf-8"), hashlib.sha256).hexdigest()
    return SignedManifest(manifest_id, payload, fingerprint(key), signature)


def verify_manifest(signed: SignedManifest, trusted_key: str) -> str:
    body = json.dumps({"manifest_id": signed.manifest_id, "payload": signed.payload}, sort_keys=True)
    expected = hmac.new(trusted_key.encode("utf-8"), body.encode("utf-8"), hashlib.sha256).hexdigest()
    if signed.signature == expected and signed.key_fingerprint == fingerprint(trusted_key):
        return "AUTHORIZED"
    return "SKULL_LOCK"


def run_policy() -> dict[str, Any]:
    payload = {
        "requested_action": "dry_run_review_quarantine_remap",
        "target": "Q_3",
        "execution_mode": "dry_run",
    }

    legacy_target_key = legacy_key(LEGACY_PUBLIC_SEED)
    legacy_attacker_key = legacy_key(LEGACY_PUBLIC_SEED)
    legacy_forged = sign_manifest("LEGACY-FORGED-001", payload, legacy_attacker_key)
    legacy_decision = verify_manifest(legacy_forged, legacy_target_key)

    hardened_target_key = hkdf_like_key(LEGACY_PUBLIC_SEED, PRIVATE_SYSTEM_SALT)
    hardened_attacker_key = hkdf_like_key(LEGACY_PUBLIC_SEED, ATTACKER_WRONG_SALT)
    hardened_forged = sign_manifest("HARDENED-FORGED-001", payload, hardened_attacker_key)
    hardened_decision = verify_manifest(hardened_forged, hardened_target_key)

    policy_checks = {
        "public_only_seed_rejected": legacy_decision == "AUTHORIZED",
        "private_salt_required": hardened_attacker_key != hardened_target_key,
        "hardened_forgery_locked": hardened_decision == "SKULL_LOCK",
        "live_command_signed": False,
        "hardware_authority": False,
    }

    return {
        "schema_version": "hqa.bacl_entropy_policy.v0",
        "execution_mode": "local_policy_proof",
        "legacy_public_seed_demo": {
            "seed_public": True,
            "attacker_key_matched": legacy_attacker_key == legacy_target_key,
            "forged_manifest_decision": legacy_decision,
            "finding": "Legacy deterministic public-only seeding is insecure.",
        },
        "hardened_hkdf_salt_demo": {
            "seed_public": True,
            "private_salt_required": True,
            "attacker_key_matched": hardened_attacker_key == hardened_target_key,
            "forged_manifest_decision": hardened_decision,
            "finding": "Private salt prevents telemetry-only key recovery.",
        },
        "policy_checks": policy_checks,
        "decision_rule": "Reject any manifest-signing scheme where public telemetry alone can regenerate signing authority.",
        "hardware_authority": False,
        "jobs_submitted": 0,
        "boundary": "BACL Entropy Policy V0 is a local red-team policy proof. It signs no live commands, reads no external secrets, submits no jobs, and grants no HAL authority.",
    }


def write_outputs(payload: dict[str, Any]) -> None:
    JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    JSON_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        "# HQA BACL Entropy Policy V0",
        "",
        "## Purpose",
        "",
        "This report captures a red-team finding: public telemetry must never be sufficient to derive manifest-signing authority.",
        "",
        "## Legacy Finding",
        "",
        f"- Attacker key matched target: `{payload['legacy_public_seed_demo']['attacker_key_matched']}`",
        f"- Forged manifest decision: `{payload['legacy_public_seed_demo']['forged_manifest_decision']}`",
        f"- Finding: {payload['legacy_public_seed_demo']['finding']}",
        "",
        "## Hardened Finding",
        "",
        f"- Private salt required: `{payload['hardened_hkdf_salt_demo']['private_salt_required']}`",
        f"- Attacker key matched target: `{payload['hardened_hkdf_salt_demo']['attacker_key_matched']}`",
        f"- Forged manifest decision: `{payload['hardened_hkdf_salt_demo']['forged_manifest_decision']}`",
        f"- Finding: {payload['hardened_hkdf_salt_demo']['finding']}",
        "",
        "## Policy Rule",
        "",
        payload["decision_rule"],
        "",
        "## Boundary",
        "",
        payload["boundary"],
        "",
    ]
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    payload = run_policy()
    write_outputs(payload)
    print(f"HQA BACL entropy policy written: {REPORT_PATH}")
    print(f"- legacy forged decision: {payload['legacy_public_seed_demo']['forged_manifest_decision']}")
    print(f"- hardened forged decision: {payload['hardened_hkdf_salt_demo']['forged_manifest_decision']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
