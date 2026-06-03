"""IBM backend calibration snapshot for HQA V2.

This script uses IBM Quantum credentials from environment variables only. It
does not read credential files, print secrets, submit jobs, reserve hardware,
run circuits, or grant HQA live hardware authority.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import statistics
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


HQA_V2_ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = HQA_V2_ROOT / "logs" / "ibm_backend_calibration_snapshot.json"
REPORT_PATH = HQA_V2_ROOT / "reports" / "HQA_IBM_BACKEND_CALIBRATION_SNAPSHOT.md"


@dataclass(frozen=True)
class BackendCalibrationSnapshot:
    backend_name: str
    timestamp_utc: str
    qubits: int
    coupling_edges: int
    mean_t1_us: float | None
    mean_t2_us: float | None
    mean_readout_error: float | None
    degraded_qubits: int
    degraded_fraction: float | None
    thresholds: dict[str, float]


@dataclass(frozen=True)
class SnapshotRun:
    package_available: bool
    token_env_present: bool
    instance_env_present: bool
    requested_backend: str | None
    excluded_backends: list[str]
    backend_selected: str | None
    operational_backends_seen: list[str]
    snapshot_performed: bool
    snapshot: BackendCalibrationSnapshot | None
    error: str | None
    hardware_authority: bool
    jobs_submitted: int


def present(value: str | None) -> bool:
    return bool(value and value.strip())


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


def get_num_qubits(backend: Any, config: Any, props: Any) -> int:
    for obj, attr in [(backend, "num_qubits"), (config, "num_qubits"), (config, "n_qubits")]:
        value = getattr(obj, attr, None) if obj is not None else None
        if value is not None:
            return int(value() if callable(value) else value)
    qubits = getattr(props, "qubits", None)
    return len(qubits or [])


def get_coupling_edges(config: Any) -> int:
    coupling = getattr(config, "coupling_map", None) if config is not None else None
    if callable(coupling):
        coupling = coupling()
    return len(coupling or [])


def prop_value(prop: Any) -> float | None:
    value = getattr(prop, "value", None)
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def collect_qubit_metrics(props: Any) -> tuple[list[float], list[float], list[float]]:
    t1: list[float] = []
    t2: list[float] = []
    readout_error: list[float] = []
    for qubit_props in getattr(props, "qubits", []) or []:
        for prop in qubit_props:
            name = str(getattr(prop, "name", "")).lower()
            value = prop_value(prop)
            if value is None:
                continue
            if name == "t1":
                t1.append(value * 1_000_000.0 if value < 1 else value)
            elif name == "t2":
                t2.append(value * 1_000_000.0 if value < 1 else value)
            elif name == "readout_error":
                readout_error.append(value)
    return t1, t2, readout_error


def mean(values: list[float]) -> float | None:
    return round(statistics.fmean(values), 6) if values else None


def count_degraded(t1: list[float], t2: list[float], readout: list[float], thresholds: dict[str, float]) -> int:
    total = max(len(t1), len(t2), len(readout))
    degraded = 0
    for index in range(total):
        t1_value = t1[index] if index < len(t1) else None
        t2_value = t2[index] if index < len(t2) else None
        readout_value = readout[index] if index < len(readout) else None
        if (
            (t1_value is not None and t1_value < thresholds["t1_min_us"])
            or (t2_value is not None and t2_value < thresholds["t2_min_us"])
            or (readout_value is not None and readout_value > thresholds["readout_max"])
        ):
            degraded += 1
    return degraded


def choose_backend(backends: list[Any], requested: str | None, excluded: set[str]) -> Any | None:
    named = {as_name(backend): backend for backend in backends}
    if requested:
        return named.get(requested)
    for backend in backends:
        if as_name(backend) not in excluded:
            return backend
    return None


def snapshot_backend(backend: Any, thresholds: dict[str, float]) -> BackendCalibrationSnapshot:
    name = as_name(backend)
    config = get_config(backend)
    props = get_properties(backend)
    if props is None:
        raise RuntimeError(f"Backend `{name}` did not return calibration properties.")
    qubits = get_num_qubits(backend, config, props)
    edges = get_coupling_edges(config)
    t1, t2, readout = collect_qubit_metrics(props)
    degraded = count_degraded(t1, t2, readout, thresholds)
    degraded_fraction = round(degraded / qubits, 6) if qubits else None
    return BackendCalibrationSnapshot(
        backend_name=name,
        timestamp_utc=datetime.now(timezone.utc).isoformat(),
        qubits=qubits,
        coupling_edges=edges,
        mean_t1_us=mean(t1),
        mean_t2_us=mean(t2),
        mean_readout_error=mean(readout),
        degraded_qubits=degraded,
        degraded_fraction=degraded_fraction,
        thresholds=thresholds,
    )


def run_snapshot(args: argparse.Namespace) -> SnapshotRun:
    package_available = importlib.util.find_spec("qiskit_ibm_runtime") is not None
    token = os.getenv("IBM_QUANTUM_TOKEN")
    instance = os.getenv("IBM_QUANTUM_INSTANCE_CRN")
    token_present = present(token)
    instance_present = present(instance)
    excluded = {item.strip() for item in args.exclude if item.strip()}

    if not package_available:
        return SnapshotRun(False, token_present, instance_present, args.backend, sorted(excluded), None, [], False, None, "qiskit_ibm_runtime is not installed.", False, 0)
    if not token_present or not instance_present:
        return SnapshotRun(True, token_present, instance_present, args.backend, sorted(excluded), None, [], False, None, "IBM_QUANTUM_TOKEN and IBM_QUANTUM_INSTANCE_CRN must both be set.", False, 0)

    try:
        from qiskit_ibm_runtime import QiskitRuntimeService

        service = QiskitRuntimeService(token=token, instance=instance)
        backends = service.backends(operational=True)
        names = [as_name(backend) for backend in backends]
        selected = choose_backend(backends, args.backend, excluded)
        if selected is None:
            return SnapshotRun(True, True, True, args.backend, sorted(excluded), None, names, False, None, "No selectable operational backend matched constraints.", False, 0)
        thresholds = {
            "t1_min_us": args.t1_min_us,
            "t2_min_us": args.t2_min_us,
            "readout_max": args.readout_max,
        }
        snapshot = snapshot_backend(selected, thresholds)
        return SnapshotRun(True, True, True, args.backend, sorted(excluded), snapshot.backend_name, names, True, snapshot, None, False, 0)
    except Exception as exc:  # pragma: no cover - live service dependent.
        return SnapshotRun(True, token_present, instance_present, args.backend, sorted(excluded), None, [], False, None, f"{type(exc).__name__}: {exc}", False, 0)


def write_outputs(run: SnapshotRun) -> None:
    JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    JSON_PATH.write_text(json.dumps(asdict(run), indent=2), encoding="utf-8")

    lines = [
        "# HQA IBM Backend Calibration Snapshot",
        "",
        "## Purpose",
        "",
        "This report captures current IBM Quantum backend calibration metadata for HQA shadow analysis.",
        "",
        "Credentials are read only from environment variables. No credentials are printed, stored, committed, or packaged.",
        "",
        "## Run Status",
        "",
        f"- `qiskit_ibm_runtime` installed: `{run.package_available}`",
        f"- `IBM_QUANTUM_TOKEN` present: `{run.token_env_present}`",
        f"- `IBM_QUANTUM_INSTANCE_CRN` present: `{run.instance_env_present}`",
        f"- Snapshot performed: `{run.snapshot_performed}`",
        f"- Backend selected: `{run.backend_selected}`",
        f"- Excluded backends: `{', '.join(run.excluded_backends) or '-'}`",
        f"- Jobs submitted: `{run.jobs_submitted}`",
        f"- Hardware authority: `{run.hardware_authority}`",
        "",
    ]
    if run.operational_backends_seen:
        lines.extend(["## Operational Backends Seen", ""])
        for name in run.operational_backends_seen:
            lines.append(f"- `{name}`")
        lines.append("")
    if run.snapshot:
        snap = run.snapshot
        lines.extend(
            [
                "## Calibration Snapshot",
                "",
                f"- Backend: `{snap.backend_name}`",
                f"- Timestamp UTC: `{snap.timestamp_utc}`",
                f"- Qubits: `{snap.qubits}`",
                f"- Coupling edges: `{snap.coupling_edges}`",
                f"- Mean T1: `{snap.mean_t1_us}` us",
                f"- Mean T2: `{snap.mean_t2_us}` us",
                f"- Mean readout error: `{snap.mean_readout_error}`",
                f"- Degraded qubits: `{snap.degraded_qubits}`",
                f"- Degraded fraction: `{snap.degraded_fraction}`",
                "",
                "Thresholds:",
                "",
                f"- T1 minimum: `{snap.thresholds['t1_min_us']}` us",
                f"- T2 minimum: `{snap.thresholds['t2_min_us']}` us",
                f"- Readout error maximum: `{snap.thresholds['readout_max']}`",
                "",
            ]
        )
    if run.error:
        lines.extend(["## Error", "", f"`{run.error}`", ""])
    lines.extend(
        [
            "## Boundary",
            "",
            "This snapshot reads backend calibration metadata only. It does not submit jobs, run circuits, reserve hardware, validate production quantum behavior, or grant HQA live hardware authority.",
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Capture IBM backend calibration metadata without submitting jobs.")
    parser.add_argument("--backend", help="Specific backend name to snapshot.")
    parser.add_argument("--exclude", action="append", default=["ibm_marrakesh"], help="Backend name to avoid. Can be used multiple times.")
    parser.add_argument("--t1-min-us", type=float, default=100.0)
    parser.add_argument("--t2-min-us", type=float, default=40.0)
    parser.add_argument("--readout-max", type=float, default=0.03)
    args = parser.parse_args()

    run = run_snapshot(args)
    write_outputs(run)
    print(f"HQA IBM calibration snapshot written: {REPORT_PATH}")
    print(f"- backend selected: {run.backend_selected}")
    print(f"- snapshot performed: {run.snapshot_performed}")
    print(f"- jobs submitted: {run.jobs_submitted}")
    if run.snapshot:
        print(f"- qubits: {run.snapshot.qubits}")
        print(f"- mean T1 us: {run.snapshot.mean_t1_us}")
        print(f"- mean T2 us: {run.snapshot.mean_t2_us}")
        print(f"- mean readout error: {run.snapshot.mean_readout_error}")
        print(f"- degraded qubits: {run.snapshot.degraded_qubits}")
    if run.error:
        print(f"- error: {run.error}")
    return 1 if run.error else 0


if __name__ == "__main__":
    sys.exit(main())
