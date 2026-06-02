"""Provider normalization matrix for HQA V2.

This module proves that HQA can accept different quantum-provider telemetry
dialects through one bounded shadow adapter shape. It does not import provider
SDKs, contact cloud services, submit jobs, read credentials, or authorize HAL
control.
"""

from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


HQA_V2_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = HQA_V2_ROOT / "logs" / "provider_normalization_matrix_v0.json"
REPORT_PATH = HQA_V2_ROOT / "reports" / "HQA_PROVIDER_NORMALIZATION_MATRIX_V0.md"


@dataclass(frozen=True)
class ProviderFixture:
    provider: str
    source_backend: str
    provider_lane: str
    topology_family: str
    collection_mode: str
    raw_fields: dict[str, Any]


@dataclass(frozen=True)
class NormalizedProviderPacket:
    schema_version: str
    provider: str
    source_backend: str
    provider_lane: str
    topology_family: str
    hqa_interpretation: str
    normalized_features: dict[str, Any]
    adapter_boundary: str
    hardware_authority: bool
    credential_access: bool


TOPOLOGY_INTERPRETATION = {
    "heavy_hex": "IBM-style sparse heavy-hex calibration is interpreted as node health plus coupling risk.",
    "grid_lattice": "Planar grid/lattice data is interpreted as local patch health plus neighborhood rupture risk.",
    "bosonic_cat": "Cat-qubit solver data is interpreted as oscillator/parity health plus photon-loss or phase-bias risk.",
    "neutral_graph": "Aggregator or runtime metadata is interpreted only from declared graph and result fields.",
}


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def provider_fixtures() -> list[ProviderFixture]:
    return [
        ProviderFixture(
            provider="ibm_qiskit_runtime",
            source_backend="ibm_marrakesh_shadow",
            provider_lane="real_qpu_calibration",
            topology_family="heavy_hex",
            collection_mode="calibration_derived_shadow",
            raw_fields={
                "qubits": 156,
                "mean_t1_us": 188.47,
                "mean_t2_us": 105.89,
                "mean_readout_error": 0.02681,
                "degraded_qubits": 55,
                "coupling_edges_pruned": 78,
            },
        ),
        ProviderFixture(
            provider="aws_braket",
            source_backend="braket_multi_provider_shadow",
            provider_lane="aggregated_device_metadata",
            topology_family="neutral_graph",
            collection_mode="provider_metadata_shadow",
            raw_fields={
                "declared_qubits": 84,
                "device_status": "ONLINE",
                "connectivity_supplied": True,
                "queue_depth_hint": 12,
                "shots": 4096,
            },
        ),
        ProviderFixture(
            provider="azure_quantum",
            source_backend="azure_provider_shadow",
            provider_lane="aggregated_workspace_metadata",
            topology_family="neutral_graph",
            collection_mode="provider_metadata_shadow",
            raw_fields={
                "provider_family": "multi_provider",
                "declared_qubits": 64,
                "resource_estimation_available": True,
                "workspace_mode": "shadow_only",
                "shots": 2048,
            },
        ),
        ProviderFixture(
            provider="nvidia_cuda_q",
            source_backend="cuda_q_local_shadow",
            provider_lane="hybrid_runtime_simulation",
            topology_family="neutral_graph",
            collection_mode="simulator_export",
            raw_fields={
                "gpu_accelerated": True,
                "kernel_count": 3,
                "samples": 8192,
                "compile_status": "simulated_success",
                "latency_budget_ms": 250,
            },
        ),
        ProviderFixture(
            provider="cirq_qsim",
            source_backend="qsim_grid_shadow",
            provider_lane="grid_circuit_simulation",
            topology_family="grid_lattice",
            collection_mode="simulator_export",
            raw_fields={
                "grid_rows": 9,
                "grid_cols": 6,
                "depth": 42,
                "two_qubit_error_proxy": 0.011,
                "local_patch_alerts": 4,
            },
        ),
        ProviderFixture(
            provider="qutip_dynamiqs",
            source_backend="cat_solver_shadow",
            provider_lane="bosonic_solver_simulation",
            topology_family="bosonic_cat",
            collection_mode="solver_export",
            raw_fields={
                "alpha": 1.35,
                "photon_loss_rate": 0.004,
                "phase_bias_ratio": 8.5,
                "parity_persistence": 0.91,
                "combined_fidelity": 0.9495,
            },
        ),
    ]


def normalize_fixture(fixture: ProviderFixture) -> NormalizedProviderPacket:
    raw = fixture.raw_fields
    feature_hash = sha256_text(json.dumps(raw, sort_keys=True))
    common_features = {
        "source_hash": feature_hash,
        "collection_mode": fixture.collection_mode,
        "risk_inputs": {},
        "topology_inputs": {},
        "latency_inputs": {},
    }

    if fixture.topology_family == "heavy_hex":
        qubits = int(raw["qubits"])
        degraded = int(raw["degraded_qubits"])
        pruned = int(raw["coupling_edges_pruned"])
        common_features["risk_inputs"] = {
            "defect_density": round(degraded / qubits, 6),
            "readout_error": raw["mean_readout_error"],
            "coherence_floor_us": min(raw["mean_t1_us"], raw["mean_t2_us"]),
        }
        common_features["topology_inputs"] = {
            "node_count": qubits,
            "degraded_nodes": degraded,
            "pruned_edges": pruned,
            "family": "heavy_hex",
        }
    elif fixture.topology_family == "grid_lattice":
        rows = int(raw["grid_rows"])
        cols = int(raw["grid_cols"])
        common_features["risk_inputs"] = {
            "patch_alert_density": round(raw["local_patch_alerts"] / (rows * cols), 6),
            "two_qubit_error_proxy": raw["two_qubit_error_proxy"],
            "depth": raw["depth"],
        }
        common_features["topology_inputs"] = {
            "node_count": rows * cols,
            "grid_rows": rows,
            "grid_cols": cols,
            "family": "grid_lattice",
        }
    elif fixture.topology_family == "bosonic_cat":
        common_features["risk_inputs"] = {
            "photon_loss_rate": raw["photon_loss_rate"],
            "phase_bias_ratio": raw["phase_bias_ratio"],
            "parity_persistence": raw["parity_persistence"],
            "combined_fidelity": raw["combined_fidelity"],
        }
        common_features["topology_inputs"] = {
            "node_count": 1,
            "mode_family": "bosonic_cat",
            "alpha": raw["alpha"],
        }
    else:
        common_features["risk_inputs"] = {
            "declared_qubits": raw.get("declared_qubits"),
            "metadata_complete": bool(raw),
            "queue_depth_hint": raw.get("queue_depth_hint"),
        }
        common_features["topology_inputs"] = {
            "node_count": raw.get("declared_qubits"),
            "family": "neutral_graph",
            "connectivity_supplied": raw.get("connectivity_supplied"),
        }
        common_features["latency_inputs"] = {
            "latency_budget_ms": raw.get("latency_budget_ms"),
            "shots_or_samples": raw.get("shots", raw.get("samples")),
        }

    return NormalizedProviderPacket(
        schema_version="hqa.provider_normalization_packet.v0",
        provider=fixture.provider,
        source_backend=fixture.source_backend,
        provider_lane=fixture.provider_lane,
        topology_family=fixture.topology_family,
        hqa_interpretation=TOPOLOGY_INTERPRETATION[fixture.topology_family],
        normalized_features=common_features,
        adapter_boundary=(
            "Provider adapter normalizes telemetry only. It does not access credentials, "
            "submit live jobs, alter pulse schedules, or authorize hardware control."
        ),
        hardware_authority=False,
        credential_access=False,
    )


def run_matrix() -> dict[str, Any]:
    packets = [normalize_fixture(fixture) for fixture in provider_fixtures()]
    payload = {
        "schema_version": "hqa.provider_normalization_matrix.v0",
        "execution_mode": "shadow_normalization_only",
        "hardware_authority": False,
        "credential_access": False,
        "provider_count": len(packets),
        "providers": [packet.provider for packet in packets],
        "topology_families": sorted({packet.topology_family for packet in packets}),
        "packets": [asdict(packet) for packet in packets],
        "boundary": (
            "This matrix validates provider-dialect normalization only. It does not prove "
            "provider performance, physical quantum control, live cloud access, or production QEC."
        ),
    }
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def write_report(payload: dict[str, Any]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# HQA Provider Normalization Matrix V0",
        "",
        "## Purpose",
        "",
        "This report verifies that HQA can receive major quantum-provider telemetry dialects through one shadow adapter grammar.",
        "",
        "The adapter matrix is deliberately offline. It uses representative fixtures only, reads no credentials, submits no jobs, and grants no hardware authority.",
        "",
        "## Coverage",
        "",
        f"- Providers covered: `{payload['provider_count']}`",
        f"- Topology families covered: `{', '.join(payload['topology_families'])}`",
        f"- Execution mode: `{payload['execution_mode']}`",
        f"- Hardware authority: `{payload['hardware_authority']}`",
        f"- Credential access: `{payload['credential_access']}`",
        "",
        "| Provider | Lane | Topology Family | HQA Interpretation |",
        "|---|---|---|---|",
    ]
    for packet in payload["packets"]:
        lines.append(
            f"| `{packet['provider']}` | `{packet['provider_lane']}` | `{packet['topology_family']}` | {packet['hqa_interpretation']} |"
        )

    lines.extend(
        [
            "",
            "## Boundary",
            "",
            payload["boundary"],
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    payload = run_matrix()
    write_report(payload)
    print(f"HQA provider normalization matrix written: {REPORT_PATH}")
    print(f"Providers normalized: {payload['provider_count']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
