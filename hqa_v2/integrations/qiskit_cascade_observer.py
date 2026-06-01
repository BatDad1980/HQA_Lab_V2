"""Qiskit cascade-observation proxy for HQA V2.

This lane is intentionally local and dry-run by default. It builds a small
syndrome-measurement circuit, defines a correlated-noise manifest, and emits a
deterministic syndrome history that HQA can analyze as a cascade trace.

The purpose is not to validate physical hardware. The purpose is to preserve
the data shape HQA needs: seed error, syndrome clicks over time, correlated
spread, decoder decision, and final governance action.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


HQA_V2_ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = HQA_V2_ROOT / "reports" / "HQA_QISKIT_CASCADE_OBSERVER.md"
JSONL_PATH = HQA_V2_ROOT / "logs" / "qiskit_cascade_syndrome_trace.jsonl"
JSON_PATH = HQA_V2_ROOT / "logs" / "qiskit_cascade_summary.json"


@dataclass
class NoiseManifest:
    single_qubit_bit_flip_rate: float
    measurement_flip_rate: float
    correlated_neighbor_rate: float
    cascade_seed: str
    boundary: str


@dataclass
class SyndromeCycle:
    cycle: int
    seed_error: str | None
    correlated_error: str | None
    syndrome_bits: str
    syndrome_weight: int
    decoder_signal: str


@dataclass
class CascadeSummary:
    qiskit_available: bool
    aer_available: bool
    dynamic_if_test_available: bool
    circuit_qubits: int
    circuit_clbits: int
    circuit_depth: int
    cycles_observed: int
    cascade_detected: bool
    quarantine_target: str
    hqa_action: str


def package_available(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def build_dynamic_circuit_probe():
    from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister

    data = QuantumRegister(3, "data")
    anc = QuantumRegister(2, "syn")
    readout = ClassicalRegister(8, "s")
    qc = QuantumCircuit(data, anc, readout, name="hqa_cascade_observer")

    cursor = 0
    for _cycle in range(4):
        qc.cx(data[0], anc[0])
        qc.cx(data[1], anc[0])
        qc.cx(data[1], anc[1])
        qc.cx(data[2], anc[1])
        qc.measure(anc[0], readout[cursor])
        qc.measure(anc[1], readout[cursor + 1])
        cursor += 2
        qc.reset(anc)

    dynamic_available = False
    try:
        with qc.if_test((readout[0], 1)):
            qc.x(data[0])
        dynamic_available = True
    except Exception:
        dynamic_available = False

    return qc, dynamic_available


def build_noise_manifest() -> NoiseManifest:
    return NoiseManifest(
        single_qubit_bit_flip_rate=0.004,
        measurement_flip_rate=0.01,
        correlated_neighbor_rate=0.035,
        cascade_seed="data[1] photon-loss-proxy / bit-flip-proxy at cycle 1",
        boundary="Local simulator noise manifest only; no backend job submitted.",
    )


def deterministic_syndrome_trace() -> list[SyndromeCycle]:
    raw = [
        (0, None, None, "00"),
        (1, "data[1]", None, "11"),
        (2, None, "data[2]", "10"),
        (3, None, "data[0]", "01"),
    ]

    trace: list[SyndromeCycle] = []
    for cycle, seed_error, correlated_error, syndrome_bits in raw:
        weight = syndrome_bits.count("1")
        if cycle == 0:
            signal = "BASELINE_CLEAR"
        elif weight >= 2:
            signal = "CASCADE_SEED_DETECTED"
        elif correlated_error:
            signal = "CORRELATED_SPREAD_OBSERVED"
        else:
            signal = "MONITOR"
        trace.append(
            SyndromeCycle(
                cycle=cycle,
                seed_error=seed_error,
                correlated_error=correlated_error,
                syndrome_bits=syndrome_bits,
                syndrome_weight=weight,
                decoder_signal=signal,
            )
        )
    return trace


def summarize(qc, dynamic_available: bool, trace: list[SyndromeCycle]) -> CascadeSummary:
    cascade_detected = any(c.decoder_signal == "CASCADE_SEED_DETECTED" for c in trace)
    return CascadeSummary(
        qiskit_available=True,
        aer_available=package_available("qiskit_aer"),
        dynamic_if_test_available=dynamic_available,
        circuit_qubits=qc.num_qubits,
        circuit_clbits=qc.num_clbits,
        circuit_depth=qc.depth(),
        cycles_observed=len(trace),
        cascade_detected=cascade_detected,
        quarantine_target="data[1]" if cascade_detected else "none",
        hqa_action="SENTINEL_QUARANTINE_AND_REROUTE_PROPOSAL" if cascade_detected else "NO_ACTION",
    )


def write_outputs(noise: NoiseManifest, trace: list[SyndromeCycle], summary: CascadeSummary) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    JSONL_PATH.parent.mkdir(parents=True, exist_ok=True)

    with JSONL_PATH.open("w", encoding="utf-8") as handle:
        for cycle in trace:
            handle.write(json.dumps(asdict(cycle)) + "\n")

    JSON_PATH.write_text(
        json.dumps(
            {
                "noise_manifest": asdict(noise),
                "summary": asdict(summary),
                "trace_path": str(JSONL_PATH),
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    lines = [
        "# HQA Qiskit Cascade Observer",
        "",
        "## Purpose",
        "",
        "This report demonstrates a local Qiskit-facing cascade observation lane for HQA V2.",
        "",
        "Instead of reducing the experiment to a final state, the observer emits a cycle-by-cycle syndrome history that HQA can treat as cascade evidence.",
        "",
        "## Readiness",
        "",
        f"- Qiskit available: `{summary.qiskit_available}`",
        f"- Qiskit Aer available: `{summary.aer_available}`",
        f"- Dynamic `if_test` construction available: `{summary.dynamic_if_test_available}`",
        f"- Circuit qubits: `{summary.circuit_qubits}`",
        f"- Circuit classical bits: `{summary.circuit_clbits}`",
        f"- Circuit depth: `{summary.circuit_depth}`",
        "",
        "## Noise Manifest",
        "",
        f"- Single-qubit bit-flip proxy rate: `{noise.single_qubit_bit_flip_rate}`",
        f"- Measurement-flip proxy rate: `{noise.measurement_flip_rate}`",
        f"- Correlated-neighbor proxy rate: `{noise.correlated_neighbor_rate}`",
        f"- Cascade seed: `{noise.cascade_seed}`",
        "",
        "## Syndrome Trace",
        "",
        "| Cycle | Syndrome | Seed Error | Correlated Error | Decoder Signal |",
        "|---:|---:|---|---|---|",
    ]

    for cycle in trace:
        lines.append(
            f"| {cycle.cycle} | `{cycle.syndrome_bits}` | {cycle.seed_error or '-'} | {cycle.correlated_error or '-'} | {cycle.decoder_signal} |"
        )

    lines.extend(
        [
            "",
            "## HQA Decision",
            "",
            f"- Cascade detected: `{summary.cascade_detected}`",
            f"- Quarantine target: `{summary.quarantine_target}`",
            f"- HQA action: `{summary.hqa_action}`",
            "",
            "## Boundary",
            "",
            "This observer is a local simulator-facing proxy. It does not submit live IBM jobs, validate physical quantum hardware, prove production QEC performance, or grant HQA hardware control authority.",
            "",
        ]
    )

    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    if not package_available("qiskit"):
        summary = CascadeSummary(
            qiskit_available=False,
            aer_available=package_available("qiskit_aer"),
            dynamic_if_test_available=False,
            circuit_qubits=0,
            circuit_clbits=0,
            circuit_depth=0,
            cycles_observed=0,
            cascade_detected=False,
            quarantine_target="none",
            hqa_action="QISKIT_UNAVAILABLE",
        )
        write_outputs(build_noise_manifest(), [], summary)
        print(f"HQA Qiskit cascade observer written: {REPORT_PATH}")
        print("- qiskit unavailable; wrote dry unavailable report.")
        return 0

    qc, dynamic_available = build_dynamic_circuit_probe()
    trace = deterministic_syndrome_trace()
    noise = build_noise_manifest()
    summary = summarize(qc, dynamic_available, trace)
    write_outputs(noise, trace, summary)
    print(f"HQA Qiskit cascade observer written: {REPORT_PATH}")
    print(f"- cascade detected: {summary.cascade_detected}")
    print(f"- quarantine target: {summary.quarantine_target}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
