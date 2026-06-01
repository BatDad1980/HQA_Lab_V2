"""Define the cat-qubit solver evidence contract for HQA V2.

This contract prepares the bosonic/cat-qubit lane without pretending a solver
has run. It defines the minimum evidence a QuTiP or Dynamiqs/JAX adapter must
emit before HQA may map cat-qubit cascade data into the risk field.
"""

from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


HQA_V2_ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = HQA_V2_ROOT / "logs" / "cat_solver_contract_v0.json"
REPORT_PATH = HQA_V2_ROOT / "reports" / "HQA_CAT_SOLVER_CONTRACT_V0.md"


@dataclass(frozen=True)
class EvidenceField:
    name: str
    field_type: str
    required: bool
    purpose: str


@dataclass(frozen=True)
class SolverContract:
    schema_version: str
    execution_mode: str
    hardware_authority: bool
    accepted_solvers: list[str]
    required_fields: list[EvidenceField]
    hqa_mapping_rules: dict[str, str]
    rejection_rules: list[str]
    boundary: str


REQUIRED_FIELDS = [
    EvidenceField(
        name="solver_name",
        field_type="string",
        required=True,
        purpose="Identifies the bosonic/open-system solver used.",
    ),
    EvidenceField(
        name="solver_version",
        field_type="string",
        required=True,
        purpose="Records solver version for replay and dependency review.",
    ),
    EvidenceField(
        name="trajectory_id",
        field_type="string",
        required=True,
        purpose="Binds all observables to one simulated trajectory or ensemble.",
    ),
    EvidenceField(
        name="cycles",
        field_type="integer",
        required=True,
        purpose="Correction-cycle count represented in the evidence.",
    ),
    EvidenceField(
        name="parity_history",
        field_type="array[number]",
        required=True,
        purpose="Cycle-indexed parity expectation or parity measurement proxy.",
    ),
    EvidenceField(
        name="photon_loss_events",
        field_type="array[object]",
        required=True,
        purpose="Trajectory-indexed photon-loss or jump records.",
    ),
    EvidenceField(
        name="logical_error_proxy",
        field_type="object",
        required=True,
        purpose="Bit-flip and phase-flip proxy scores with confidence.",
    ),
    EvidenceField(
        name="wigner_metadata",
        field_type="object",
        required=True,
        purpose="Compact phase-space metadata without storing heavy image arrays.",
    ),
    EvidenceField(
        name="cascade_indicator",
        field_type="string",
        required=True,
        purpose="LOW_ACTIVITY, WATCHLIST, or CASCADE_LIKE classification.",
    ),
    EvidenceField(
        name="confidence",
        field_type="number[0,1]",
        required=True,
        purpose="Confidence that the solver evidence supports the cascade classification.",
    ),
]


def build_contract() -> SolverContract:
    return SolverContract(
        schema_version="hqa.cat_solver_contract.v0",
        execution_mode="contract_only",
        hardware_authority=False,
        accepted_solvers=["qutip", "dynamiqs_jax"],
        required_fields=REQUIRED_FIELDS,
        hqa_mapping_rules={
            "parity_history": "maps to syndrome persistence and cycle pressure",
            "photon_loss_events": "maps to seed error and jump-density pressure",
            "logical_error_proxy": "maps to risk-field syndrome pressure",
            "wigner_metadata": "maps to phase-space stability notes only",
            "cascade_indicator": "maps to LOW_ACTIVITY, WATCHLIST, or CASCADE_LIKE risk labels",
            "confidence": "bounds the contribution of solver-derived evidence",
        },
        rejection_rules=[
            "Reject evidence with unknown solver_name.",
            "Reject evidence without solver_version.",
            "Reject evidence when parity_history length differs from cycles.",
            "Reject confidence outside [0, 1].",
            "Reject attempts to request live hardware, pulse changes, or HAL execution.",
            "Reject heavy binary/image arrays in the evidence packet; store metadata only.",
        ],
        boundary="Contract-only lane. It defines required solver evidence but does not run bosonic simulation, validate physical cat-qubit hardware, or grant live control authority.",
    )


def write_outputs(contract: SolverContract) -> None:
    CONTRACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = asdict(contract)
    CONTRACT_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        "# HQA Cat Solver Contract V0",
        "",
        "## Purpose",
        "",
        "This report defines the evidence contract a future cat-qubit solver adapter must satisfy before its output can feed HQA risk-field logic.",
        "",
        "The contract is intentionally solver-agnostic. It supports QuTiP and Dynamiqs/JAX lanes without making either dependency mandatory for the base HQA regression.",
        "",
        "## Contract Summary",
        "",
        f"- Schema version: `{contract.schema_version}`",
        f"- Execution mode: `{contract.execution_mode}`",
        f"- Hardware authority: `{contract.hardware_authority}`",
        f"- Accepted solvers: `{', '.join(contract.accepted_solvers)}`",
        "",
        "## Required Evidence Fields",
        "",
        "| Field | Type | Required | Purpose |",
        "|---|---|---:|---|",
    ]
    for field in contract.required_fields:
        lines.append(f"| `{field.name}` | `{field.field_type}` | `{field.required}` | {field.purpose} |")

    lines.extend(["", "## HQA Mapping Rules", ""])
    for key, value in contract.hqa_mapping_rules.items():
        lines.append(f"- `{key}`: {value}")

    lines.extend(["", "## Rejection Rules", ""])
    for rule in contract.rejection_rules:
        lines.append(f"- {rule}")

    lines.extend(
        [
            "",
            "## Boundary",
            "",
            contract.boundary,
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    contract = build_contract()
    write_outputs(contract)
    print(f"HQA cat solver contract written: {CONTRACT_PATH}")
    print(f"HQA cat solver contract report written: {REPORT_PATH}")
    print(f"- required fields: {len(contract.required_fields)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
