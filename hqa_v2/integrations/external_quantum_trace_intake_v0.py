"""External quantum trace intake contract for HQA V2.

This module defines and exercises the safe intake shape for real or vendor-
provided quantum telemetry. It does not contact external services. Its job is
to prove that HQA has a strict front door before external traces can be mapped
into topology, syndrome, risk-field, or proposal artifacts.
"""

from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


HQA_V2_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_ROOT = HQA_V2_ROOT / "outputs" / "external_trace_intake_v0"
CONTRACT_PATH = HQA_V2_ROOT / "logs" / "external_quantum_trace_intake_contract_v0.json"
REPORT_PATH = HQA_V2_ROOT / "reports" / "HQA_EXTERNAL_QUANTUM_TRACE_INTAKE_V0.md"


@dataclass(frozen=True)
class IntakeField:
    name: str
    field_type: str
    required: bool
    purpose: str


@dataclass(frozen=True)
class IntakeDecision:
    trace_id: str
    source_vendor: str
    accepted: bool
    normalized: bool
    rejection_reasons: list[str]
    output_file: str | None


REQUIRED_FIELDS = [
    IntakeField("trace_id", "string", True, "Stable identifier for this external trace."),
    IntakeField("source_vendor", "string", True, "Vendor or backend family label."),
    IntakeField("source_backend", "string", True, "Backend/device/simulator label."),
    IntakeField("topology_family", "string", True, "Chip/topology family used for HQA compensation."),
    IntakeField("collection_mode", "string", True, "public_sample, vendor_shadow, simulator_export, or hardware_export."),
    IntakeField("timestamp_utc", "string", True, "Trace timestamp or export timestamp."),
    IntakeField("topology_nodes", "array[object]", True, "Node health/coherence records."),
    IntakeField("topology_edges", "array[object]", True, "Coupling/connectivity records."),
    IntakeField("syndrome_records", "array[object]", True, "Cycle-indexed syndrome observations."),
    IntakeField("provenance", "object", True, "Source, license, permission, and redaction metadata."),
]

ALLOWED_VENDORS = {"ibm", "alice_bob", "google", "neutral_vendor", "local_simulator"}
ALLOWED_MODES = {"public_sample", "vendor_shadow", "simulator_export", "hardware_export"}
TOPOLOGY_PROFILES = {
    "heavy_hex": {
        "family": "heavy_hex",
        "typical_vendor": "ibm",
        "connectivity_model": "sparse_fixed_frequency_lattice",
        "degree_baseline": 2.4,
        "coupling_floor": 0.55,
        "role_bias": "data_ancilla_readout",
        "risk_bias": "watch correlated edge activity and readout-adjacent syndrome persistence",
    },
    "grid_lattice": {
        "family": "grid_lattice",
        "typical_vendor": "google",
        "connectivity_model": "nearest_neighbor_planar_grid",
        "degree_baseline": 3.2,
        "coupling_floor": 0.50,
        "role_bias": "data_coupler_readout",
        "risk_bias": "watch neighborhood clusters and local patch rupture",
    },
    "bosonic_cat": {
        "family": "bosonic_cat",
        "typical_vendor": "alice_bob",
        "connectivity_model": "oscillator_mode_with_ancilla_controls",
        "degree_baseline": 1.8,
        "coupling_floor": 0.45,
        "role_bias": "mode_ancilla_readout",
        "risk_bias": "watch parity persistence, photon-loss events, and masked ancilla faults",
    },
    "neutral_graph": {
        "family": "neutral_graph",
        "typical_vendor": "neutral_vendor",
        "connectivity_model": "vendor_supplied_graph",
        "degree_baseline": 2.0,
        "coupling_floor": 0.40,
        "role_bias": "unknown_until_declared",
        "risk_bias": "use declared topology only; do not infer hardware physics",
    },
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def build_contract() -> dict[str, Any]:
    return {
        "schema_version": "hqa.external_quantum_trace_intake.v0",
        "execution_mode": "intake_validation_only",
        "hardware_authority": False,
        "allowed_vendors": sorted(ALLOWED_VENDORS),
        "allowed_collection_modes": sorted(ALLOWED_MODES),
        "allowed_topology_families": sorted(TOPOLOGY_PROFILES),
        "required_fields": [asdict(field) for field in REQUIRED_FIELDS],
        "rejection_rules": [
            "Reject unknown source_vendor labels.",
            "Reject unknown topology_family labels.",
            "Reject traces without provenance.permission_basis.",
            "Reject traces containing secrets, API keys, credentials, or unredacted account identifiers.",
            "Reject topology nodes with coherence_score outside [0, 1].",
            "Reject topology edges with coupling_score outside [0, 1].",
            "Reject syndrome records with confidence outside [0, 1].",
            "Reject syndrome records with non-binary syndrome_bits.",
            "Reject any trace requesting live backend execution, pulse changes, or HAL action.",
        ],
        "normalization_targets": [
            "hqa.topology_snapshot.v1",
            "hqa.syndrome_record.v1",
            "hqa.topology_compensation.v0",
            "hqa.risk_field.v0",
            "hqa.shadow_advisory",
        ],
        "boundary": "External trace intake validates and normalizes data only. It does not contact vendors, submit jobs, validate physical quantum performance, or authorize hardware control.",
    }


def clean_string(value: Any) -> str:
    return str(value).strip().lower()


def has_secret_text(payload: dict[str, Any]) -> bool:
    text = json.dumps(payload, sort_keys=True).lower()
    needles = ["api_key", "apikey", "password", "token=", "secret", "credential", "bearer "]
    return any(needle in text for needle in needles)


def validate_trace(trace: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for field in REQUIRED_FIELDS:
        if field.required and field.name not in trace:
            errors.append(f"missing required field `{field.name}`")

    vendor = clean_string(trace.get("source_vendor", ""))
    mode = clean_string(trace.get("collection_mode", ""))
    topology_family = clean_string(trace.get("topology_family", ""))
    if vendor not in ALLOWED_VENDORS:
        errors.append(f"unknown source_vendor `{trace.get('source_vendor')}`")
    if mode not in ALLOWED_MODES:
        errors.append(f"unknown collection_mode `{trace.get('collection_mode')}`")
    if topology_family not in TOPOLOGY_PROFILES:
        errors.append(f"unknown topology_family `{trace.get('topology_family')}`")
    provenance = trace.get("provenance", {})
    if not isinstance(provenance, dict) or not provenance.get("permission_basis"):
        errors.append("missing provenance.permission_basis")
    if has_secret_text(trace):
        errors.append("secret-like content detected")

    for node in trace.get("topology_nodes", []):
        score = node.get("coherence_score")
        if not isinstance(score, (int, float)) or isinstance(score, bool) or not 0.0 <= score <= 1.0:
            errors.append(f"invalid coherence_score for node `{node.get('node_id')}`")
    for edge in trace.get("topology_edges", []):
        score = edge.get("coupling_score")
        if not isinstance(score, (int, float)) or isinstance(score, bool) or not 0.0 <= score <= 1.0:
            errors.append(f"invalid coupling_score for edge `{edge.get('source')}`-`{edge.get('target')}`")
    for record in trace.get("syndrome_records", []):
        bits = str(record.get("syndrome_bits", ""))
        confidence = record.get("confidence", 0.0)
        if not bits or any(bit not in "01" for bit in bits):
            errors.append(f"invalid syndrome_bits for record `{record.get('record_id')}`")
        if not isinstance(confidence, (int, float)) or isinstance(confidence, bool) or not 0.0 <= confidence <= 1.0:
            errors.append(f"invalid confidence for record `{record.get('record_id')}`")

    forbidden_requests = ["live_backend_execution", "pulse_change", "hal_execution"]
    requested = trace.get("requested_actions", [])
    if any(action in requested for action in forbidden_requests):
        errors.append("trace requested forbidden live authority")
    return errors


def normalize_trace(trace: dict[str, Any]) -> dict[str, Any]:
    vendor = clean_string(trace["source_vendor"])
    topology_family = clean_string(trace["topology_family"])
    trace_id = str(trace["trace_id"])
    profile = TOPOLOGY_PROFILES[topology_family]
    node_count = len(trace["topology_nodes"])
    edge_count = len(trace["topology_edges"])
    observed_degree = round((edge_count * 2) / node_count, 6) if node_count else 0.0
    compensation = {
        "schema_version": "hqa.topology_compensation.v0",
        "topology_family": topology_family,
        "connectivity_model": profile["connectivity_model"],
        "degree_baseline": profile["degree_baseline"],
        "observed_degree": observed_degree,
        "coupling_floor": profile["coupling_floor"],
        "role_bias": profile["role_bias"],
        "risk_bias": profile["risk_bias"],
        "normalization_rule": "Map vendor topology into HQA node/edge graph; adjust interpretation thresholds by family metadata without changing HQA risk/proposal APIs.",
        "boundary": "Compensation metadata changes interpretation only. It does not authorize live calibration, pulse changes, or topology edits.",
    }
    topology = {
        "schema_version": "hqa.topology_snapshot.v1",
        "snapshot_id": f"EXT-TOPO-{trace_id}",
        "timestamp_utc": str(trace["timestamp_utc"]),
        "nodes": [
            {
                "node_id": str(node["node_id"]),
                "status": str(node.get("status", "unknown")),
                "coherence_score": round(float(node["coherence_score"]), 6),
                "role": str(node.get("role", "unknown")),
            }
            for node in trace["topology_nodes"]
        ],
        "edges": [
            {
                "source": str(edge["source"]),
                "target": str(edge["target"]),
                "coupling_score": round(float(edge["coupling_score"]), 6),
            }
            for edge in trace["topology_edges"]
        ],
    }
    syndromes = []
    for index, record in enumerate(trace["syndrome_records"]):
        syndromes.append(
            {
                "schema_version": "hqa.syndrome_record.v1",
                "record_id": str(record.get("record_id", f"EXT-SYN-{trace_id}-{index}")),
                "cycle": int(record["cycle"]),
                "source_lane": "hardware_shadow" if trace["collection_mode"] == "hardware_export" else "manual_fixture",
                "syndrome_bits": str(record["syndrome_bits"]),
                "seed_error": record.get("seed_error"),
                "correlated_error": record.get("correlated_error"),
                "decoder_signal": str(record["decoder_signal"]),
                "confidence": round(float(record.get("confidence", 0.0)), 6),
            }
        )
    return {
        "schema_version": "hqa.external_trace_normalized.v0",
        "trace_id": trace_id,
        "source_vendor": vendor,
        "source_backend": str(trace["source_backend"]),
        "topology_family": topology_family,
        "collection_mode": str(trace["collection_mode"]),
        "hardware_authority": False,
        "topology_compensation": compensation,
        "topology_snapshot": topology,
        "syndrome_records": syndromes,
        "provenance": trace["provenance"],
        "boundary": "Normalized external trace only. No live backend job, pulse change, or HAL execution is authorized.",
    }


def sample_traces() -> list[dict[str, Any]]:
    return [
        {
            "trace_id": "TRACE-IBM-SHADOW-001",
            "source_vendor": "ibm",
            "source_backend": "sample_heavy_hex_shadow",
            "topology_family": "heavy_hex",
            "collection_mode": "public_sample",
            "timestamp_utc": "2026-06-01T00:00:00Z",
            "topology_nodes": [
                {"node_id": "Q_0", "status": "healthy", "coherence_score": 0.95, "role": "data"},
                {"node_id": "Q_1", "status": "degraded", "coherence_score": 0.48, "role": "data"},
                {"node_id": "Q_2", "status": "healthy", "coherence_score": 0.91, "role": "ancilla"},
            ],
            "topology_edges": [
                {"source": "Q_0", "target": "Q_1", "coupling_score": 0.76},
                {"source": "Q_1", "target": "Q_2", "coupling_score": 0.71},
            ],
            "syndrome_records": [
                {
                    "record_id": "EXT-SYN-001",
                    "cycle": 7,
                    "syndrome_bits": "1110",
                    "seed_error": "Q_1",
                    "correlated_error": "Q_0",
                    "decoder_signal": "CASCADE_LIKE_HISTORY",
                    "confidence": 0.84,
                }
            ],
            "provenance": {
                "permission_basis": "public_or_authorized_shadow_sample",
                "redacted": True,
                "notes": "Synthetic shape matching expected external trace format.",
            },
            "requested_actions": [],
        },
        {
            "trace_id": "TRACE-REJECT-SECRET-001",
            "source_vendor": "unknown_lab",
            "source_backend": "private_box",
            "topology_family": "unknown_shape",
            "collection_mode": "hardware_export",
            "timestamp_utc": "2026-06-01T00:00:00Z",
            "topology_nodes": [{"node_id": "Q_0", "status": "healthy", "coherence_score": 1.2, "role": "data"}],
            "topology_edges": [],
            "syndrome_records": [{"record_id": "BAD", "cycle": 0, "syndrome_bits": "12", "decoder_signal": "BAD", "confidence": 1.4}],
            "provenance": {"redacted": False, "api_key": "DO_NOT_ACCEPT"},
            "requested_actions": ["live_backend_execution"],
        },
    ]


def run_intake() -> list[IntakeDecision]:
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    decisions: list[IntakeDecision] = []
    for trace in sample_traces():
        errors = validate_trace(trace)
        output_file: str | None = None
        if not errors:
            normalized = normalize_trace(trace)
            output_path = OUTPUT_ROOT / f"{trace['trace_id']}_normalized.json"
            write_json(output_path, normalized)
            output_file = str(output_path.relative_to(HQA_V2_ROOT))
        decisions.append(
            IntakeDecision(
                trace_id=str(trace.get("trace_id", "missing")),
                source_vendor=str(trace.get("source_vendor", "missing")),
                accepted=not errors,
                normalized=not errors,
                rejection_reasons=errors,
                output_file=output_file,
            )
        )

    manifest_lines = []
    for path in sorted(OUTPUT_ROOT.glob("*_normalized.json")):
        manifest_lines.append(f"{sha256(path)}  {path.name}")
    (OUTPUT_ROOT / "MANIFEST_SHA256.txt").write_text("\n".join(manifest_lines) + ("\n" if manifest_lines else ""), encoding="utf-8")
    return decisions


def write_outputs(decisions: list[IntakeDecision]) -> None:
    contract = build_contract()
    write_json(CONTRACT_PATH, contract)
    summary = {
        "schema_version": "hqa.external_quantum_trace_intake_run.v0",
        "execution_mode": "intake_validation_only",
        "hardware_authority": False,
        "decisions": [asdict(decision) for decision in decisions],
    }
    write_json(OUTPUT_ROOT / "intake_decisions.json", summary)

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# HQA External Quantum Trace Intake V0",
        "",
        "## Purpose",
        "",
        "This report defines and exercises the front door for external quantum telemetry before it can enter HQA risk-field logic.",
        "",
        "The intake layer validates provenance, redaction, topology bounds, syndrome bounds, and live-authority boundaries. It does not contact vendors or submit jobs.",
        "",
        "## Contract Summary",
        "",
        f"- Schema version: `{contract['schema_version']}`",
        f"- Execution mode: `{contract['execution_mode']}`",
        f"- Hardware authority: `{contract['hardware_authority']}`",
        f"- Allowed vendors: `{', '.join(contract['allowed_vendors'])}`",
        f"- Allowed topology families: `{', '.join(contract['allowed_topology_families'])}`",
        "",
        "## Intake Decisions",
        "",
        "| Trace | Vendor | Accepted | Normalized | Reasons | Output |",
        "|---|---|---:|---:|---|---|",
    ]
    for decision in decisions:
        reasons = "; ".join(decision.rejection_reasons) if decision.rejection_reasons else "-"
        lines.append(
            f"| `{decision.trace_id}` | `{decision.source_vendor}` | `{decision.accepted}` | `{decision.normalized}` | {reasons} | `{decision.output_file or '-'}` |"
        )

    lines.extend(
        [
            "",
            "## Boundary",
            "",
            contract["boundary"],
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    decisions = run_intake()
    write_outputs(decisions)
    accepted = sum(1 for decision in decisions if decision.accepted)
    print(f"HQA external trace intake report written: {REPORT_PATH}")
    print(f"- accepted: {accepted}/{len(decisions)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
