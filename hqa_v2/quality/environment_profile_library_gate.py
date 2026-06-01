"""Quality gate for HQA Environment Profile Library V0."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


HQA_V2_ROOT = Path(__file__).resolve().parents[1]
LIBRARY_PATH = HQA_V2_ROOT / "logs" / "environment_profile_library_v0.json"
REPORT_PATH = HQA_V2_ROOT / "reports" / "HQA_ENVIRONMENT_PROFILE_LIBRARY_GATE.md"

EXPECTED_CODENAMES = {"earth", "titan", "asteroid", "deep_vacuum", "pulse_breath"}


def load_payload() -> dict[str, Any]:
    return json.loads(LIBRARY_PATH.read_text(encoding="utf-8"))


def write_report(checks: list[tuple[str, bool, str]]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    passed = sum(1 for _, ok, _ in checks if ok)
    lines = [
        "# HQA Environment Profile Library Gate",
        "",
        "## Purpose",
        "",
        "This gate verifies that Environment Profile Library V0 is bounded, complete, and interpretation-only.",
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
            "This gate validates profile-library structure only. It does not validate physical quantum hardware, production QEC performance, or live HAL execution.",
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def thresholds_ordered(profile: dict[str, Any]) -> bool:
    monitor = float(profile["risk_threshold_monitor"])
    route = float(profile["risk_threshold_route_review"])
    quarantine = float(profile["risk_threshold_quarantine_review"])
    return 0.0 <= monitor < route < quarantine <= 1.0


def main() -> int:
    if not LIBRARY_PATH.exists():
        checks = [("library_exists", False, f"Missing `{LIBRARY_PATH}`")]
        write_report(checks)
        print(f"HQA environment profile library gate written: {REPORT_PATH}")
        return 1

    payload = load_payload()
    profiles = payload.get("profiles", [])
    codenames = {profile.get("internal_codename") for profile in profiles}
    all_actions = {action for profile in profiles for action in profile.get("hqa_allowed_actions", [])}
    forbidden_actions = all_actions - {
        "MONITOR_ONLY",
        "MONITOR_WITH_ROUTE_REVIEW",
        "QUARANTINE_PROPOSAL",
        "ROUTE_REVIEW_AND_QUARANTINE_PROPOSAL",
        "NO_ROUTE_HOLD_REVIEW",
    }

    checks = [
        ("schema_version", payload.get("schema_version") == "hqa.environment_profile_library.v0", "Profile library schema is V0."),
        ("interpretation_only", payload.get("execution_mode") == "interpretation_only", f"Mode: `{payload.get('execution_mode')}`."),
        ("no_hardware_authority", payload.get("hardware_authority") is False, "Library grants no hardware authority."),
        ("five_profiles_present", codenames == EXPECTED_CODENAMES, f"Codenames: `{sorted(codenames)}`."),
        ("thresholds_ordered", all(thresholds_ordered(profile) for profile in profiles), "All thresholds are bounded and ordered."),
        ("no_forbidden_actions", not forbidden_actions, f"Forbidden actions: `{sorted(forbidden_actions)}`."),
        ("deep_vacuum_holds", any(profile.get("internal_codename") == "deep_vacuum" and profile.get("hqa_allowed_actions") == ["NO_ROUTE_HOLD_REVIEW"] for profile in profiles), "Deep Vacuum maps to hold-only review."),
        ("pulse_is_overlay", any(profile.get("internal_codename") == "pulse_breath" and profile.get("simulator_mapping") == "schedule_overlay" for profile in profiles), "Pulse/Breath is an overlay profile."),
        (
            "boundaries_present",
            all(len(str(profile.get("boundary", ""))) >= 24 for profile in profiles),
            "Every profile has a substantive boundary statement.",
        ),
    ]

    write_report(checks)
    failed = [check for check in checks if not check[1]]
    print(f"HQA environment profile library gate written: {REPORT_PATH}")
    print(f"Passed {len(checks) - len(failed)}/{len(checks)} checks.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
