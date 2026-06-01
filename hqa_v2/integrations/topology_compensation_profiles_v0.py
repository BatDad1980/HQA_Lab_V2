"""Write HQA topology compensation profiles.

These profiles keep external quantum-company chip designs behind one HQA
normalization grammar. They tune interpretation metadata only; they do not
change the risk-field/proposal API for each vendor.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from external_quantum_trace_intake_v0 import TOPOLOGY_PROFILES


HQA_V2_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = HQA_V2_ROOT / "logs" / "topology_compensation_profiles_v0.json"
REPORT_PATH = HQA_V2_ROOT / "reports" / "HQA_TOPOLOGY_COMPENSATION_PROFILES_V0.md"


def write_outputs() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": "hqa.topology_compensation_profiles.v0",
        "execution_mode": "interpretation_only",
        "hardware_authority": False,
        "profiles": TOPOLOGY_PROFILES,
        "boundary": "Topology compensation profiles normalize interpretation across chip families only. They do not authorize live backend access, calibration, pulse changes, or HAL execution.",
    }
    OUTPUT_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        "# HQA Topology Compensation Profiles V0",
        "",
        "## Purpose",
        "",
        "This report defines how HQA compensates for different chip/topology families without changing its core risk-field or proposal APIs.",
        "",
        "The profile layer prevents vendor-specific geometry from becoming vendor-specific HQA logic.",
        "",
        "## Profiles",
        "",
        "| Family | Typical Vendor | Connectivity Model | Degree Baseline | Coupling Floor | Risk Bias |",
        "|---|---|---|---:|---:|---|",
    ]
    for profile in TOPOLOGY_PROFILES.values():
        lines.append(
            f"| `{profile['family']}` | `{profile['typical_vendor']}` | `{profile['connectivity_model']}` | `{profile['degree_baseline']}` | `{profile['coupling_floor']}` | {profile['risk_bias']} |"
        )
    lines.extend(
        [
            "",
            "## Rule",
            "",
            "Every external topology must be normalized into the same HQA node/edge graph and accompanied by a topology-compensation profile.",
            "",
            "This allows HQA to compare heavy-hex, grid/lattice, bosonic/cat, and neutral graph evidence without changing its evaluation angle for every company.",
            "",
            "## Boundary",
            "",
            payload["boundary"],
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    write_outputs()
    print(f"HQA topology compensation profiles written: {OUTPUT_PATH}")
    print(f"HQA topology compensation report written: {REPORT_PATH}")
    print(f"- profiles: {len(TOPOLOGY_PROFILES)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
