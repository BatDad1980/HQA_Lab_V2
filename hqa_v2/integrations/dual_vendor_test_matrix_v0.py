"""Build HQA dual vendor test matrix.

The matrix keeps cat-qubit and non-cat quantum-company evidence in separate
lanes while routing both through the same HQA intake, compensation, risk, and
shadow-review grammar.
"""

from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


HQA_V2_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = HQA_V2_ROOT / "logs" / "dual_vendor_test_matrix_v0.json"
REPORT_PATH = HQA_V2_ROOT / "reports" / "HQA_DUAL_VENDOR_TEST_MATRIX_V0.md"


@dataclass(frozen=True)
class TestLane:
    lane_id: str
    vendor_family: str
    topology_family: str
    evidence_class: str
    current_status: str
    required_next_evidence: list[str]
    hqa_entrypoint: str
    comparison_goal: str
    boundary: str


LANES = [
    TestLane(
        lane_id="CAT-ALICE-BOB",
        vendor_family="alice_bob",
        topology_family="bosonic_cat",
        evidence_class="cat_qubit_solver_or_authorized_hardware_trace",
        current_status="contract_ready_model_evidence_present",
        required_next_evidence=[
            "authorized cat-qubit solver output or hardware export",
            "parity history",
            "photon-loss events",
            "logical error proxy",
            "Wigner metadata summary",
            "confidence-bounded cascade indicator",
        ],
        hqa_entrypoint="cat_solver_contract_v0 -> external_trace_intake_v0 -> topology_compensation",
        comparison_goal="Compare static alpha/control parameters against HQA-adapted alpha/control proposals under asymmetric X/Z noise.",
        boundary="Cat lane must not be described as Alice & Bob physical validation until authorized physical cat-qubit traces exist.",
    ),
    TestLane(
        lane_id="IBM-HEAVY-HEX",
        vendor_family="ibm",
        topology_family="heavy_hex",
        evidence_class="calibration_derived_topology_and_syndrome_trace",
        current_status="candidate_calibration_derived_result_present",
        required_next_evidence=[
            "redacted backend calibration export",
            "defect/quarantine list",
            "coupling map before and after pruning",
            "routing comparison trace",
            "provenance and permission basis",
        ],
        hqa_entrypoint="external_trace_intake_v0 -> topology_compensation -> risk_field -> shadow_proposal",
        comparison_goal="Compare default routing against HQA quarantine/reroute posture on heavy-hex calibration data.",
        boundary="IBM lane should distinguish physical calibration access from local noisy simulation comparison.",
    ),
    TestLane(
        lane_id="GOOGLE-GRID",
        vendor_family="google",
        topology_family="grid_lattice",
        evidence_class="grid_or_lattice_topology_trace",
        current_status="intake_ready_no_authorized_trace_yet",
        required_next_evidence=[
            "authorized grid/lattice topology export",
            "cycle-indexed syndrome or error proxy records",
            "coupling/edge health records",
            "provenance and permission basis",
        ],
        hqa_entrypoint="external_trace_intake_v0 -> topology_compensation -> risk_field -> shadow_proposal",
        comparison_goal="Evaluate whether HQA risk ranking remains stable on planar grid/lattice neighborhood rupture patterns.",
        boundary="Google lane remains schema-ready only until authorized trace data exists.",
    ),
    TestLane(
        lane_id="NEUTRAL-VENDOR-GRAPH",
        vendor_family="neutral_vendor",
        topology_family="neutral_graph",
        evidence_class="vendor_declared_graph_trace",
        current_status="schema_ready",
        required_next_evidence=[
            "declared node/edge graph",
            "declared health metrics",
            "syndrome or error-history trace",
            "provenance and permission basis",
        ],
        hqa_entrypoint="external_trace_intake_v0 -> topology_compensation -> risk_field -> shadow_proposal",
        comparison_goal="Test HQA without inferring undocumented hardware physics from the vendor graph.",
        boundary="Neutral lane uses declared topology only and does not infer substrate physics.",
    ),
]


def write_outputs() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": "hqa.dual_vendor_test_matrix.v0",
        "execution_mode": "planning_and_readiness_only",
        "hardware_authority": False,
        "lanes": [asdict(lane) for lane in LANES],
        "boundary": "The matrix coordinates evidence lanes only. It does not contact vendors, submit jobs, claim physical validation, or authorize live hardware action.",
    }
    OUTPUT_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        "# HQA Dual Vendor Test Matrix V0",
        "",
        "## Purpose",
        "",
        "This report defines HQA's dual testing strategy: cat-qubit evidence in one lane, and non-cat vendor topology/syndrome evidence in parallel lanes.",
        "",
        "The goal is to test HQA against different chip designs without changing HQA's core evaluation angle for each company.",
        "",
        "## Test Lanes",
        "",
        "| Lane | Vendor Family | Topology Family | Current Status | HQA Entrypoint |",
        "|---|---|---|---|---|",
    ]
    for lane in LANES:
        lines.append(
            f"| `{lane.lane_id}` | `{lane.vendor_family}` | `{lane.topology_family}` | `{lane.current_status}` | `{lane.hqa_entrypoint}` |"
        )

    lines.extend(["", "## Required Next Evidence", ""])
    for lane in LANES:
        lines.append(f"### `{lane.lane_id}`")
        lines.append("")
        for item in lane.required_next_evidence:
            lines.append(f"- {item}")
        lines.append("")
        lines.append(f"Comparison goal: {lane.comparison_goal}")
        lines.append("")
        lines.append(f"Boundary: {lane.boundary}")
        lines.append("")

    lines.extend(
        [
            "## Boundary",
            "",
            payload["boundary"],
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    write_outputs()
    print(f"HQA dual vendor test matrix written: {OUTPUT_PATH}")
    print(f"HQA dual vendor report written: {REPORT_PATH}")
    print(f"- lanes: {len(LANES)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
