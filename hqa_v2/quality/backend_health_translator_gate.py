"""Quality gate for HQA Backend Health Translator V0."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


HQA_V2_ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = HQA_V2_ROOT / "logs" / "backend_health_translator_v0.json"
REPORT_PATH = HQA_V2_ROOT / "reports" / "HQA_BACKEND_HEALTH_TRANSLATOR_GATE.md"


def write_report(checks: list[tuple[str, bool, str]]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    passed = sum(1 for _, ok, _ in checks)
    lines = [
        "# HQA Backend Health Translator Gate",
        "",
        "## Purpose",
        "",
        "This gate verifies that backend calibration evidence is translated into a provider-neutral HQA health grammar without granting hardware authority.",
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
            "This gate validates shadow health translation only. It does not validate production QEC, submit provider jobs, run circuits, change pulses, or authorize HAL execution.",
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    if not INPUT_PATH.exists():
        checks = [("translator_output_exists", False, "Run backend_health_translator_v0.py first.")]
        write_report(checks)
        print(f"HQA backend health translator gate written: {REPORT_PATH}")
        return 1

    payload: dict[str, Any] = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
    profiles = payload.get("profiles", [])
    by_backend = {profile.get("source_backend"): profile for profile in profiles}
    comparison = payload.get("comparison", {})
    hints = {profile.get("intervention_hint") for profile in profiles}

    checks = [
        ("schema_version", payload.get("schema_version") == "hqa.backend_health_translator.v0", "Translator schema is V0."),
        ("shadow_only", payload.get("execution_mode") == "shadow_translation_only", f"Mode: `{payload.get('execution_mode')}`."),
        ("no_hardware_authority", payload.get("hardware_authority") is False and all(profile.get("hardware_authority") is False for profile in profiles), "No profile grants hardware authority."),
        ("no_jobs_submitted", payload.get("jobs_submitted") == 0 and all(profile.get("jobs_submitted") == 0 for profile in profiles), "Translation submitted zero jobs."),
        ("two_ibm_backends_present", {"ibm_kingston", "ibm_fez"}.issubset(by_backend), f"Backends: `{', '.join(sorted(str(name) for name in by_backend))}`."),
        ("normalized_health_scores", all(isinstance(profile.get("health_score"), float) and 0.0 <= profile["health_score"] <= 1.0 for profile in profiles), "Every backend has a bounded health score."),
        ("kingston_healthier_than_fez", by_backend.get("ibm_kingston", {}).get("health_score", 0) > by_backend.get("ibm_fez", {}).get("health_score", 1), "Kingston ranks healthier than Fez from captured telemetry."),
        ("fez_quarantine_hint", by_backend.get("ibm_fez", {}).get("intervention_hint") == "QUARANTINE_REMAP_SHADOW", "Fez maps to shadow quarantine/remap pressure."),
        ("kingston_monitor_hint", by_backend.get("ibm_kingston", {}).get("intervention_hint") == "MONITOR_WITH_SHADOW_OPTIMIZATION", "Kingston maps to monitor/shadow optimization."),
        ("backend_name_not_policy", comparison.get("translation_rule") == "Select behavior from normalized health profile, not backend name.", "Comparison states provider-neutral translation rule."),
        ("spatial_limitation_honest", all(profile.get("spatial_visibility") is False and "per-qubit" in profile.get("spatial_limitation", "") for profile in profiles), "Summary snapshots do not overclaim spatial clustering visibility."),
        ("boundary_present", "does not submit jobs" in payload.get("boundary", "") and "authorize HAL execution" in payload.get("boundary", ""), "Boundary blocks jobs and HAL execution."),
    ]

    write_report(checks)
    failed = [check for check in checks if not check[1]]
    print(f"HQA backend health translator gate written: {REPORT_PATH}")
    print(f"Passed {len(checks) - len(failed)}/{len(checks)} checks.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
