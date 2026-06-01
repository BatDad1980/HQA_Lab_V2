"""Unified optional simulator facade for HQA V2.

The facade provides a small common API for available simulator lanes without
making those packages mandatory at import time.
"""

from __future__ import annotations

import importlib.util
import time
from dataclasses import dataclass
from typing import Any


@dataclass
class SimulatorRunResult:
    backend: str
    runtime_s: float
    result: dict[str, int]
    boundary: str


class SimulatorUnavailable(RuntimeError):
    """Raised when an optional simulator backend is unavailable."""


def package_available(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


class BaseSimulatorFacade:
    name = "base"
    required_imports: tuple[str, ...] = ()

    def __init__(self, shots: int = 1024) -> None:
        self.shots = shots
        missing = [name for name in self.required_imports if not package_available(name)]
        if missing:
            raise SimulatorUnavailable(f"{self.name} unavailable; missing imports: {', '.join(missing)}")

    def build_bell_circuit(self) -> Any:
        raise NotImplementedError

    def run(self, circuit: Any) -> SimulatorRunResult:
        raise NotImplementedError


class QiskitAerFacade(BaseSimulatorFacade):
    name = "qiskit_aer"
    required_imports = ("qiskit", "qiskit_aer")

    def build_bell_circuit(self):
        from qiskit import QuantumCircuit

        circuit = QuantumCircuit(2, 2)
        circuit.h(0)
        circuit.cx(0, 1)
        circuit.measure([0, 1], [0, 1])
        return circuit

    def run(self, circuit) -> SimulatorRunResult:
        from qiskit import transpile
        from qiskit_aer import AerSimulator

        simulator = AerSimulator()
        started = time.perf_counter()
        compiled = transpile(circuit, simulator)
        result = simulator.run(compiled, shots=self.shots, seed_simulator=123).result()
        elapsed = time.perf_counter() - started
        counts = {str(key): int(value) for key, value in result.get_counts().items()}
        return SimulatorRunResult(
            backend="qiskit_aer",
            runtime_s=elapsed,
            result=counts,
            boundary="Local Aer simulation only; no live backend job submitted.",
        )


class CirqFacade(BaseSimulatorFacade):
    name = "cirq"
    required_imports = ("cirq",)

    def __init__(self, shots: int = 1024) -> None:
        super().__init__(shots=shots)
        import cirq

        if package_available("qsimcirq"):
            try:
                from qsimcirq import QSimSimulator

                self.simulator = QSimSimulator()
                self.backend_name = "qsimcirq"
            except Exception:
                self.simulator = cirq.Simulator()
                self.backend_name = "cirq"
        else:
            self.simulator = cirq.Simulator()
            self.backend_name = "cirq"

    def build_bell_circuit(self):
        import cirq

        q0, q1 = cirq.LineQubit.range(2)
        return cirq.Circuit(
            cirq.H(q0),
            cirq.CNOT(q0, q1),
            cirq.measure(q0, q1, key="m"),
        )

    def run(self, circuit) -> SimulatorRunResult:
        started = time.perf_counter()
        result = self.simulator.run(circuit, repetitions=self.shots)
        elapsed = time.perf_counter() - started
        counts: dict[str, int] = {}
        for row in result.measurements["m"]:
            key = "".join(str(int(bit)) for bit in row)
            counts[key] = counts.get(key, 0) + 1
        return SimulatorRunResult(
            backend=self.backend_name,
            runtime_s=elapsed,
            result=counts,
            boundary="Local Cirq/qsim simulation only; no live backend job submitted.",
        )


SIMULATORS = {
    "qiskit_aer": QiskitAerFacade,
    "qiskit": QiskitAerFacade,
    "cirq": CirqFacade,
}


def get_simulator(name: str, shots: int = 1024) -> BaseSimulatorFacade:
    key = name.lower()
    if key not in SIMULATORS:
        raise ValueError(f"Unknown simulator backend: {name}")
    return SIMULATORS[key](shots=shots)


def available_simulators() -> dict[str, bool]:
    return {
        "qiskit_aer": all(package_available(name) for name in QiskitAerFacade.required_imports),
        "cirq": all(package_available(name) for name in CirqFacade.required_imports),
    }
