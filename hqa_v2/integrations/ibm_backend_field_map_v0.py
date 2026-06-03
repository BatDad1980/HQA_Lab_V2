"""IBM backend field-map adapter for HQA V2.

The calibration snapshot answers "how healthy is this backend overall?"  This
field-map adapter answers the next question: "where are the weak neighborhoods?"

Default execution uses a local fixture so regression stays offline. Live IBM
metadata capture is opt-in with --live and still submits zero jobs.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


HQA_V2_ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = HQA_V2_ROOT / "logs" / "ibm_backend_field_map_v0.json"
REPORT_PATH = HQA_V2_ROOT / "reports" / "HQA_IBM_BACKEND_FIELD_MAP_V0.md"


THRESHOLDS = {
    "t1_min_us": 100.0,
    "t2_min_us": 40.0,
    "readout_max": 0.03,
}


@dataclass(frozen=True)
class QubitField:
    index: int
    t1_us: float | None
    t2_us: float | None
    readout_error: float | None
    status: str
    reasons: list[str]


@dataclass(frozen=True)
class EdgeField:
    source: int
    target: int
    status: str
    endpoint_degraded_count: int
    coupling_risk: float


def present(value: str | None) -> bool:
    return bool(value and value.strip())


def prop_value(prop: Any) -> float | None:
    value = getattr(prop, "value", None)
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def as_name(backend: Any) -> str:
    name = getattr(backend, "name", None)
    if callable(name):
        return str(name())
    if name:
        return str(name)
    return str(backend)


def get_config(backend: Any) -> Any:
    config = getattr(backend, "configuration", None)
    return config() if callable(config) else config


def get_properties(backend: Any) -> Any:
    props = getattr(backend, "properties", None)
    return props() if callable(props) else props


def get_coupling_edges(config: Any) -> list[tuple[int, int]]:
    coupling = getattr(config, "coupling_map", None) if config is not None else None
    if callable(coupling):
        coupling = coupling()
    edges: list[tuple[int, int]] = []
    for edge in coupling or []:
        try:
            source, target = int(edge[0]), int(edge[1])
        except (TypeError, ValueError, IndexError):
            continue
        edges.append((source, target))
    return edges


def classify_qubit(index: int, t1_us: float | None, t2_us: float | None, readout_error: float | None) -> QubitField:
    reasons: list[str] = []
    if t1_us is not None and t1_us < THRESHOLDS["t1_min_us"]:
        reasons.append("weak_t1")
    if t2_us is not None and t2_us < THRESHOLDS["t2_min_us"]:
        reasons.append("weak_t2")
    if readout_error is not None and readout_error > THRESHOLDS["readout_max"]:
        reasons.append("high_readout_error")
    return QubitField(
        index=index,
        t1_us=t1_us,
        t2_us=t2_us,
        readout_error=readout_error,
        status="degraded" if reasons else "healthy",
        reasons=reasons,
    )


def collect_qubit_fields(props: Any) -> list[QubitField]:
    fields: list[QubitField] = []
    for index, qubit_props in enumerate(getattr(props, "qubits", []) or []):
        values: dict[str, float] = {}
        for prop in qubit_props:
            name = str(getattr(prop, "name", "")).lower()
            value = prop_value(prop)
            if value is None:
                continue
            if name in {"t1", "t2"}:
                values[name] = value * 1_000_000.0 if value < 1 else value
            elif name == "readout_error":
                values[name] = value
        fields.append(
            classify_qubit(
                index=index,
                t1_us=values.get("t1"),
                t2_us=values.get("t2"),
                readout_error=values.get("readout_error"),
            )
        )
    return fields


def classify_edges(edges: list[tuple[int, int]], qubits: list[QubitField]) -> list[EdgeField]:
    degraded = {qubit.index for qubit in qubits if qubit.status == "degraded"}
    edge_fields: list[EdgeField] = []
    for source, target in edges:
        endpoint_degraded_count = int(source in degraded) + int(target in degraded)
        status = "degraded_neighborhood" if endpoint_degraded_count else "healthy"
        coupling_risk = round(endpoint_degraded_count / 2.0, 6)
        edge_fields.append(EdgeField(source, target, status, endpoint_degraded_count, coupling_risk))
    return edge_fields


def cluster_proxy(qubits: list[QubitField], edges: list[EdgeField]) -> dict[str, Any]:
    degraded = {qubit.index for qubit in qubits if qubit.status == "degraded"}
    if not degraded:
        return {"degraded_clusters_visible": True, "largest_degraded_component": 0, "degraded_edge_count": 0}
    adjacency: dict[int, set[int]] = {index: set() for index in degraded}
    degraded_edge_count = 0
    for edge in edges:
        if edge.source in degraded and edge.target in degraded:
            degraded_edge_count += 1
            adjacency[edge.source].add(edge.target)
            adjacency[edge.target].add(edge.source)
    seen: set[int] = set()
    largest = 0
    for node in degraded:
        if node in seen:
            continue
        stack = [node]
        component_size = 0
        while stack:
            current = stack.pop()
            if current in seen:
                continue
            seen.add(current)
            component_size += 1
            stack.extend(adjacency[current] - seen)
        largest = max(largest, component_size)
    return {
        "degraded_clusters_visible": True,
        "largest_degraded_component": largest,
        "degraded_edge_count": degraded_edge_count,
    }


def fixture_payload() -> dict[str, Any]:
    qubits = [
        classify_qubit(0, 170.0, 115.0, 0.018),
        classify_qubit(1, 92.0, 102.0, 0.019),
        classify_qubit(2, 166.0, 31.0, 0.021),
        classify_qubit(3, 171.0, 104.0, 0.041),
        classify_qubit(4, 162.0, 100.0, 0.024),
        classify_qubit(5, 168.0, 111.0, 0.017),
    ]
    edges = classify_edges([(0, 1), (1, 2), (2, 3), (3, 4), (4, 5)], qubits)
    return build_payload(
        source_backend="ibm_fixture_heavy_hex_patch",
        collection_mode="offline_fixture",
        qubits=qubits,
        edges=edges,
        live_check_performed=False,
        token_env_present=present(os.getenv("IBM_QUANTUM_TOKEN")),
        instance_env_present=present(os.getenv("IBM_QUANTUM_INSTANCE_CRN")),
    )


def choose_backend(backends: list[Any], requested: str | None) -> Any | None:
    named = {as_name(backend): backend for backend in backends}
    if requested:
        return named.get(requested)
    return backends[0] if backends else None


def live_payload(args: argparse.Namespace) -> dict[str, Any]:
    if importlib.util.find_spec("qiskit_ibm_runtime") is None:
        raise RuntimeError("qiskit_ibm_runtime is not installed.")
    token = os.getenv("IBM_QUANTUM_TOKEN")
    instance = os.getenv("IBM_QUANTUM_INSTANCE_CRN")
    if not present(token) or not present(instance):
        raise RuntimeError("IBM_QUANTUM_TOKEN and IBM_QUANTUM_INSTANCE_CRN must both be set.")
    from qiskit_ibm_runtime import QiskitRuntimeService

    service = QiskitRuntimeService(token=token, instance=instance)
    backends = service.backends(operational=True)
    selected = choose_backend(backends, args.backend)
    if selected is None:
        raise RuntimeError("No operational IBM backend was available.")
    props = get_properties(selected)
    if props is None:
        raise RuntimeError(f"Backend `{as_name(selected)}` did not return calibration properties.")
    qubits = collect_qubit_fields(props)
    edges = classify_edges(get_coupling_edges(get_config(selected)), qubits)
    return build_payload(
        source_backend=as_name(selected),
        collection_mode="live_metadata_snapshot",
        qubits=qubits,
        edges=edges,
        live_check_performed=True,
        token_env_present=True,
        instance_env_present=True,
    )


def build_payload(
    source_backend: str,
    collection_mode: str,
    qubits: list[QubitField],
    edges: list[EdgeField],
    live_check_performed: bool,
    token_env_present: bool,
    instance_env_present: bool,
) -> dict[str, Any]:
    degraded_count = sum(1 for qubit in qubits if qubit.status == "degraded")
    degraded_edges = sum(1 for edge in edges if edge.status == "degraded_neighborhood")
    return {
        "schema_version": "hqa.ibm_backend_field_map.v0",
        "provider": "ibm_qiskit_runtime",
        "source_backend": source_backend,
        "topology_family": "heavy_hex",
        "collection_mode": collection_mode,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "live_check_performed": live_check_performed,
        "token_env_present": token_env_present,
        "instance_env_present": instance_env_present,
        "hardware_authority": False,
        "jobs_submitted": 0,
        "thresholds": THRESHOLDS,
        "qubits": [qubit.__dict__ for qubit in qubits],
        "edges": [edge.__dict__ for edge in edges],
        "summary": {
            "qubit_count": len(qubits),
            "edge_count": len(edges),
            "degraded_qubits": degraded_count,
            "degraded_fraction": round(degraded_count / len(qubits), 6) if qubits else None,
            "degraded_neighborhood_edges": degraded_edges,
            "degraded_neighborhood_edge_fraction": round(degraded_edges / len(edges), 6) if edges else None,
            **cluster_proxy(qubits, edges),
        },
        "boundary": "IBM field-map capture reads calibration metadata only. It submits zero jobs, runs zero circuits, changes no pulse schedules, and grants no HAL authority.",
    }


def write_outputs(payload: dict[str, Any]) -> None:
    JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    JSON_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    summary = payload["summary"]
    lines = [
        "# HQA IBM Backend Field Map V0",
        "",
        "## Purpose",
        "",
        "This report captures the richer field-map layer HQA needs to distinguish averages from damaged neighborhoods.",
        "",
        "## Summary",
        "",
        f"- Source backend: `{payload['source_backend']}`",
        f"- Collection mode: `{payload['collection_mode']}`",
        f"- Live check performed: `{payload['live_check_performed']}`",
        f"- Hardware authority: `{payload['hardware_authority']}`",
        f"- Jobs submitted: `{payload['jobs_submitted']}`",
        f"- Qubits mapped: `{summary['qubit_count']}`",
        f"- Edges mapped: `{summary['edge_count']}`",
        f"- Degraded qubits: `{summary['degraded_qubits']}`",
        f"- Degraded neighborhood edges: `{summary['degraded_neighborhood_edges']}`",
        f"- Largest degraded component: `{summary['largest_degraded_component']}`",
        "",
        "## Boundary",
        "",
        payload["boundary"],
        "",
    ]
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build an HQA IBM backend field map without submitting jobs.")
    parser.add_argument("--live", action="store_true", help="Opt in to live IBM metadata capture using environment credentials.")
    parser.add_argument("--backend", help="Specific IBM backend name for live metadata capture.")
    args = parser.parse_args()
    payload = live_payload(args) if args.live else fixture_payload()
    write_outputs(payload)
    print(f"HQA IBM backend field map written: {REPORT_PATH}")
    print(f"- source backend: {payload['source_backend']}")
    print(f"- collection mode: {payload['collection_mode']}")
    print(f"- jobs submitted: {payload['jobs_submitted']}")
    print(f"- degraded qubits: {payload['summary']['degraded_qubits']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
