"""Adapter skeletons for optional HQA V2 quantum simulator backends.

These classes intentionally avoid importing optional heavy dependencies at
module import time. Each adapter checks availability when used.
"""

from __future__ import annotations

import importlib.util
from dataclasses import dataclass


@dataclass
class AdapterStatus:
    name: str
    available: bool
    boundary: str


class OptionalSimulatorAdapter:
    name = "base"
    required_imports: tuple[str, ...] = ()

    def available(self) -> bool:
        return all(importlib.util.find_spec(pkg) is not None for pkg in self.required_imports)

    def status(self) -> AdapterStatus:
        return AdapterStatus(
            name=self.name,
            available=self.available(),
            boundary="Optional simulator adapter; no physical hardware control.",
        )

    def to_hqa_trace(self, payload):
        raise NotImplementedError("Adapter-specific trace conversion is not implemented yet.")


class QiskitAdapter(OptionalSimulatorAdapter):
    name = "qiskit"
    required_imports = ("qiskit",)


class CirqAdapter(OptionalSimulatorAdapter):
    name = "cirq"
    required_imports = ("cirq",)


class QutipAdapter(OptionalSimulatorAdapter):
    name = "qutip"
    required_imports = ("qutip",)


class DynamiqsAdapter(OptionalSimulatorAdapter):
    name = "dynamiqs"
    required_imports = ("dynamiqs", "jax")


def get_adapter_statuses() -> list[AdapterStatus]:
    return [
        QiskitAdapter().status(),
        CirqAdapter().status(),
        QutipAdapter().status(),
        DynamiqsAdapter().status(),
    ]

