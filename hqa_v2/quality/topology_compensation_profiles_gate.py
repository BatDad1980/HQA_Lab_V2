"""Quality gate for topology compensation profiles."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


HQA_V2_ROOT = Path(__file__).resolve().parents[1]
PROFILE_PATH = HQA_V2_ROOT / "logs" / "topology_compensation_profiles_v0.json"
INTAKE_OUTPUT = HQA_V2_ROOT / "outputs" / "external_trace_intake_v0" / "TRACE-IBM-SHADOW-001_normalized.json"
REPORT_PATH = HQA_V2_ROOT / "reports" / "HQA_TOPOLOGY_COMPENSATION_PROFILES_GATE.md"

EXPECTED_FAMILIES = {"heavy_hex", "grid_lattice", "bosonic_cat", "neutral_graph"}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_report(checks: list[tuple[str, bool, str]]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    passed = sum(1 for _, ok, _ in checks if ok)
    lines = [
        "# HQA Topology Compensation Profiles Gate",
        "",
        "## Purpose",
        "",
        "This gate verifies that topology compensation supports multiple chip families while keeping HQA interpretation-only.",
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
            "This gate validates topology-compensation metadata only. It does not validate physical quantum hardware, production QEC performance, live vendor access, or HAL execution.",
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    if not PROFILE_PATH.exists() or not INTAKE_OUTPUT.exists():
        checks = [("inputs_exist", False, "Profile or normalized intake output missing.")]
        write_report(checks)
        print(f"HQA topology compensation profiles gate written: {REPORT_PATH}")
        return 1

    profiles_payload = load_json(PROFILE_PATH)
    normalized = load_json(INTAKE_OUTPUT)
    profiles = profiles_payload.get("profiles", {})
    families = set(profiles)
    compensation = normalized.get("topology_compensation", {})

    checks = [
        ("schema_version", profiles_payload.get("schema_version") == "hqa.topology_compensation_profiles.v0", "Profile schema is V0."),
        ("interpretation_only", profiles_payload.get("execution_mode") == "interpretation_only", f"Mode: `{profiles_payload.get('execution_mode')}`."),
        ("no_hardware_authority", profiles_payload.get("hardware_authority") is False and normalized.get("hardware_authority") is False, "No compensation artifact grants hardware authority."),
        ("all_families_present", families == EXPECTED_FAMILIES, f"Families: `{sorted(families)}`."),
        ("families_have_bounds", all(0.0 <= float(profile["coupling_floor"]) <= 1.0 and float(profile["degree_baseline"]) > 0.0 for profile in profiles.values()), "All families have bounded coupling floors and positive degree baselines."),
        ("normalized_trace_has_compensation", compensation.get("schema_version") == "hqa.topology_compensation.v0", "Normalized trace includes compensation metadata."),
        ("heavy_hex_selected", normalized.get("topology_family") == "heavy_hex" and compensation.get("topology_family") == "heavy_hex", f"Normalized family: `{normalized.get('topology_family')}`."),
        ("compensation_has_observed_degree", isinstance(compensation.get("observed_degree"), (int, float)), f"Observed degree: `{compensation.get('observed_degree')}`."),
        ("risk_bias_present", bool(compensation.get("risk_bias")), "Compensation risk-bias note exists."),
        ("normalization_rule_present", "without changing HQA risk/proposal APIs" in compensation.get("normalization_rule", ""), "Normalization rule preserves HQA API."),
    ]

    write_report(checks)
    failed = [check for check in checks if not check[1]]
    print(f"HQA topology compensation profiles gate written: {REPORT_PATH}")
    print(f"Passed {len(checks) - len(failed)}/{len(checks)} checks.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
