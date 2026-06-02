"""Quality gate for HQA Provider Normalization Matrix V0."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


HQA_V2_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = HQA_V2_ROOT / "logs" / "provider_normalization_matrix_v0.json"
REPORT_PATH = HQA_V2_ROOT / "reports" / "HQA_PROVIDER_NORMALIZATION_MATRIX_GATE.md"


EXPECTED_PROVIDERS = {
    "ibm_qiskit_runtime",
    "aws_braket",
    "azure_quantum",
    "nvidia_cuda_q",
    "cirq_qsim",
    "qutip_dynamiqs",
}
EXPECTED_FAMILIES = {"heavy_hex", "grid_lattice", "bosonic_cat", "neutral_graph"}


def load_payload() -> dict[str, Any]:
    return json.loads(OUTPUT_PATH.read_text(encoding="utf-8"))


def write_report(checks: list[tuple[str, bool, str]]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    passed = sum(1 for _, ok, _ in checks)
    lines = [
        "# HQA Provider Normalization Matrix Gate",
        "",
        "## Purpose",
        "",
        "This gate verifies provider-dialect normalization coverage and boundary behavior.",
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
            "This gate validates offline normalization only. It does not validate live vendor access, physical quantum performance, provider credentials, or HAL execution.",
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    if not OUTPUT_PATH.exists():
        checks = [("matrix_exists", False, "Run provider_normalization_matrix_v0.py first.")]
        write_report(checks)
        print(f"HQA provider normalization matrix gate written: {REPORT_PATH}")
        return 1

    payload = load_payload()
    packets = payload.get("packets", [])
    providers = {packet.get("provider") for packet in packets}
    families = {packet.get("topology_family") for packet in packets}
    boundaries = " ".join(packet.get("adapter_boundary", "") for packet in packets).lower()

    checks = [
        ("schema_version", payload.get("schema_version") == "hqa.provider_normalization_matrix.v0", "Matrix schema is V0."),
        ("shadow_only", payload.get("execution_mode") == "shadow_normalization_only", f"Mode: `{payload.get('execution_mode')}`."),
        ("no_hardware_authority", payload.get("hardware_authority") is False and all(packet.get("hardware_authority") is False for packet in packets), "No packet grants hardware authority."),
        ("no_credential_access", payload.get("credential_access") is False and all(packet.get("credential_access") is False for packet in packets), "No packet reads or requires credentials."),
        ("provider_coverage", providers == EXPECTED_PROVIDERS, f"Providers: `{', '.join(sorted(str(provider) for provider in providers))}`."),
        ("topology_family_coverage", families == EXPECTED_FAMILIES, f"Families: `{', '.join(sorted(str(family) for family in families))}`."),
        ("provider_count", len(packets) == 6, f"Packets: `{len(packets)}`."),
        ("each_packet_hashed", all(packet.get("normalized_features", {}).get("source_hash") for packet in packets), "Every packet has a source hash."),
        ("ibm_defect_density", any(packet.get("provider") == "ibm_qiskit_runtime" and packet.get("normalized_features", {}).get("risk_inputs", {}).get("defect_density") == 0.352564 for packet in packets), "IBM fixture maps degraded qubits to defect density."),
        ("cat_lane_present", any(packet.get("provider") == "qutip_dynamiqs" and packet.get("topology_family") == "bosonic_cat" for packet in packets), "Bosonic/cat solver lane exists."),
        ("neutral_aggregators_present", {"aws_braket", "azure_quantum", "nvidia_cuda_q"}.issubset(providers), "Aggregator/runtime lanes are represented."),
        ("boundary_words_present", "does not access credentials" in boundaries and "submit live jobs" in boundaries and "hardware control" in boundaries, "Adapter boundaries block credentials, live jobs, and hardware control."),
    ]

    write_report(checks)
    failed = [check for check in checks if not check[1]]
    print(f"HQA provider normalization matrix gate written: {REPORT_PATH}")
    print(f"Passed {len(checks) - len(failed)}/{len(checks)} checks.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
