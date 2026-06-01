"""Local Qiskit Aer cascade-noise probe for HQA V2.

This probe uses Qiskit Aer locally with a custom noise model. It records the
full syndrome-history bitstring, not just a final state, so HQA can reason over
error propagation across cycles.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


HQA_V2_ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = HQA_V2_ROOT / "reports" / "HQA_QISKIT_AER_CASCADE_NOISE_PROBE.md"
JSON_PATH = HQA_V2_ROOT / "logs" / "qiskit_aer_cascade_noise_probe.json"
JSONL_PATH = HQA_V2_ROOT / "logs" / "qiskit_aer_syndrome_histories.jsonl"


@dataclass
class AerNoiseProbeConfig:
    profile: str
    shots: int
    seed_simulator: int
    inject_seed: bool
    measurement_flip_rate: float
    correlated_cx_xx_rate: float
    single_x_rate: float
    boundary: str


@dataclass
class SyndromeHistory:
    profile: str
    bitstring: str
    count: int
    syndrome_weight: int
    cycles_flagged: int
    hqa_decoder_signal: str


@dataclass
class AerNoiseProbeSummary:
    profile: str
    qiskit_available: bool
    aer_available: bool
    ran_local_aer: bool
    shots: int
    unique_histories: int
    cascade_like_histories: int
    cascade_like_rate: float
    dominant_history: str
    hqa_action: str
    error: str | None


def package_available(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def build_syndrome_history_circuit(inject_seed: bool):
    from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister

    data = QuantumRegister(3, "data")
    syn = QuantumRegister(2, "syn")
    bits = ClassicalRegister(8, "s")
    qc = QuantumCircuit(data, syn, bits, name="hqa_aer_cascade_noise_probe")

    cursor = 0
    if inject_seed:
        # Insert a deterministic seed proxy so the noisy simulation has
        # something to propagate around. In a hardware lane this would be
        # observed, not forced.
        qc.x(data[1])
    for _cycle in range(4):
        qc.cx(data[0], syn[0])
        qc.cx(data[1], syn[0])
        qc.cx(data[1], syn[1])
        qc.cx(data[2], syn[1])
        qc.measure(syn[0], bits[cursor])
        qc.measure(syn[1], bits[cursor + 1])
        qc.reset(syn)
        cursor += 2
    return qc


def build_noise_model(config: AerNoiseProbeConfig):
    from qiskit_aer.noise import NoiseModel, ReadoutError, pauli_error

    noise_model = NoiseModel()
    single_error = pauli_error([("X", config.single_x_rate), ("I", 1.0 - config.single_x_rate)])
    correlated_error = pauli_error(
        [("XX", config.correlated_cx_xx_rate), ("II", 1.0 - config.correlated_cx_xx_rate)]
    )
    readout_error = ReadoutError(
        [
            [1.0 - config.measurement_flip_rate, config.measurement_flip_rate],
            [config.measurement_flip_rate, 1.0 - config.measurement_flip_rate],
        ]
    )

    noise_model.add_all_qubit_quantum_error(single_error, ["x"])
    noise_model.add_all_qubit_quantum_error(correlated_error, ["cx"])
    noise_model.add_all_qubit_readout_error(readout_error)
    return noise_model


def normalize_bitstring(bitstring: str) -> str:
    return bitstring.replace(" ", "")


def cycles_flagged(bitstring: str) -> int:
    normalized = normalize_bitstring(bitstring)
    pairs = [normalized[index : index + 2] for index in range(0, len(normalized), 2)]
    return sum(1 for pair in pairs if "1" in pair)


def decoder_signal(bitstring: str) -> str:
    weight = normalize_bitstring(bitstring).count("1")
    flagged = cycles_flagged(bitstring)
    if flagged >= 3 or weight >= 4:
        return "CASCADE_LIKE_HISTORY"
    if flagged >= 2:
        return "WATCHLIST_HISTORY"
    return "LOW_ACTIVITY_HISTORY"


def summarize_counts(counts: dict[str, int], config: AerNoiseProbeConfig) -> tuple[list[SyndromeHistory], AerNoiseProbeSummary]:
    histories: list[SyndromeHistory] = []
    for bitstring, count in sorted(counts.items(), key=lambda item: item[1], reverse=True):
        normalized = normalize_bitstring(bitstring)
        histories.append(
            SyndromeHistory(
                profile=config.profile,
                bitstring=normalized,
                count=count,
                syndrome_weight=normalized.count("1"),
                cycles_flagged=cycles_flagged(normalized),
                hqa_decoder_signal=decoder_signal(normalized),
            )
        )

    cascade_like = sum(history.count for history in histories if history.hqa_decoder_signal == "CASCADE_LIKE_HISTORY")
    cascade_rate = cascade_like / config.shots if config.shots else 0.0
    dominant = histories[0].bitstring if histories else "none"
    action = "SENTINEL_REVIEW_RECOMMENDED" if cascade_rate >= 0.10 else "MONITOR_ONLY"

    return histories, AerNoiseProbeSummary(
        profile=config.profile,
        qiskit_available=True,
        aer_available=True,
        ran_local_aer=True,
        shots=config.shots,
        unique_histories=len(histories),
        cascade_like_histories=cascade_like,
        cascade_like_rate=round(cascade_rate, 6),
        dominant_history=dominant,
        hqa_action=action,
        error=None,
    )


def run_probe(config: AerNoiseProbeConfig) -> tuple[list[SyndromeHistory], AerNoiseProbeSummary]:
    from qiskit import transpile
    from qiskit_aer import AerSimulator

    circuit = build_syndrome_history_circuit(inject_seed=config.inject_seed)
    noise_model = build_noise_model(config)
    simulator = AerSimulator(noise_model=noise_model, seed_simulator=config.seed_simulator)
    compiled = transpile(circuit, simulator)
    result = simulator.run(compiled, shots=config.shots).result()
    counts = result.get_counts()
    return summarize_counts(counts, config)


def write_outputs(configs: list[AerNoiseProbeConfig], histories: list[SyndromeHistory], summaries: list[AerNoiseProbeSummary]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    JSON_PATH.parent.mkdir(parents=True, exist_ok=True)

    with JSONL_PATH.open("w", encoding="utf-8") as handle:
        for history in histories:
            handle.write(json.dumps(asdict(history)) + "\n")

    JSON_PATH.write_text(
        json.dumps(
            {
                "configs": [asdict(config) for config in configs],
                "summaries": [asdict(summary) for summary in summaries],
                "histories_path": str(JSONL_PATH),
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    lines = [
        "# HQA Qiskit Aer Cascade Noise Probe",
        "",
        "## Purpose",
        "",
        "This report demonstrates a local Aer simulator probe that preserves full syndrome-history bitstrings under a custom noise model.",
        "",
        "The probe is intended to test cascade-observation plumbing, not physical quantum hardware behavior.",
        "",
        "## Configuration",
        "",
        "| Profile | Shots | Seed Injected | Measurement Flip | Single X Proxy | Correlated CX XX Proxy |",
        "|---|---:|---:|---:|---:|---:|",
    ]

    for config in configs:
        lines.append(
            f"| `{config.profile}` | {config.shots} | `{config.inject_seed}` | `{config.measurement_flip_rate}` | `{config.single_x_rate}` | `{config.correlated_cx_xx_rate}` |"
        )

    lines.extend(
        [
        "",
        "## Results",
        "",
        "| Profile | Local Aer | Unique Histories | Cascade-Like Shots | Cascade-Like Rate | Dominant History | HQA Action |",
        "|---|---:|---:|---:|---:|---:|---|",
        ]
    )

    for summary in summaries:
        lines.append(
            f"| `{summary.profile}` | `{summary.ran_local_aer}` | {summary.unique_histories} | {summary.cascade_like_histories} | `{summary.cascade_like_rate}` | `{summary.dominant_history}` | {summary.hqa_action} |"
        )

    lines.extend(
        [
        "",
        "## Top Syndrome Histories",
        "",
        "| Rank | Profile | History | Count | Weight | Flagged Cycles | HQA Decoder Signal |",
        "|---:|---|---:|---:|---:|---:|---|",
        ]
    )

    sorted_histories = sorted(histories, key=lambda item: (item.profile, -item.count, item.bitstring))
    for rank, history in enumerate(sorted_histories[:20], start=1):
        lines.append(
            f"| {rank} | `{history.profile}` | `{history.bitstring}` | {history.count} | {history.syndrome_weight} | {history.cycles_flagged} | {history.hqa_decoder_signal} |"
        )

    errors = [summary for summary in summaries if summary.error]
    if errors:
        lines.extend(["", "## Errors", ""])
        for summary in errors:
            lines.append(f"- `{summary.profile}`: `{summary.error}`")

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "The nominal profile checks the quiet baseline. The stress profile injects a seed and correlated noise so the HQA cascade observer can verify that syndrome history, not only final-state counts, drives the decision.",
    ]
        )

    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This is a local simulator probe. It does not submit IBM jobs, validate physical quantum hardware, prove production QEC performance, or grant HQA hardware control authority.",
            "",
        ]
    )

    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def unavailable_summary(error: str) -> AerNoiseProbeSummary:
    return AerNoiseProbeSummary(
        profile="unavailable",
        qiskit_available=package_available("qiskit"),
        aer_available=package_available("qiskit_aer"),
        ran_local_aer=False,
        shots=0,
        unique_histories=0,
        cascade_like_histories=0,
        cascade_like_rate=0.0,
        dominant_history="none",
        hqa_action="SIMULATOR_UNAVAILABLE",
        error=error,
    )


def main() -> int:
    configs = [
        AerNoiseProbeConfig(
            profile="nominal",
            shots=512,
            seed_simulator=405,
            inject_seed=False,
            measurement_flip_rate=0.003,
            correlated_cx_xx_rate=0.002,
            single_x_rate=0.0005,
            boundary="Local Aer simulator only; no live backend job submitted.",
        ),
        AerNoiseProbeConfig(
            profile="stress",
            shots=512,
            seed_simulator=406,
            inject_seed=True,
            measurement_flip_rate=0.015,
            correlated_cx_xx_rate=0.025,
            single_x_rate=0.002,
            boundary="Local Aer simulator only; no live backend job submitted.",
        ),
    ]

    if not package_available("qiskit") or not package_available("qiskit_aer"):
        summary = unavailable_summary("qiskit and qiskit_aer are both required.")
        write_outputs(configs, [], [summary])
        print(f"HQA Qiskit Aer cascade noise probe written: {REPORT_PATH}")
        print("- simulator unavailable; wrote dry unavailable report.")
        return 0

    histories: list[SyndromeHistory] = []
    summaries: list[AerNoiseProbeSummary] = []
    for config in configs:
        try:
            profile_histories, summary = run_probe(config)
        except Exception as exc:
            summary = unavailable_summary(f"{type(exc).__name__}: {exc}")
            summary.profile = config.profile
            profile_histories = []
        histories.extend(profile_histories)
        summaries.append(summary)

    write_outputs(configs, histories, summaries)
    print(f"HQA Qiskit Aer cascade noise probe written: {REPORT_PATH}")
    for summary in summaries:
        print(f"- {summary.profile}: local Aer={summary.ran_local_aer}, cascade-like rate={summary.cascade_like_rate}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
