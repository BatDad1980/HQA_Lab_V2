"""Optional quantum simulator readiness check for HQA V2.

This script does not require simulator packages to be installed. It checks
whether optional integration lanes are available and writes a small report.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


HQA_V2_ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = HQA_V2_ROOT / "reports" / "HQA_SIMULATOR_READINESS.md"
JSON_PATH = HQA_V2_ROOT / "logs" / "simulator_readiness.json"


@dataclass
class PackageCheck:
    lane: str
    import_name: str
    installed: bool
    purpose: str


CHECKS = [
    PackageCheck("IBM Quantum", "qiskit", False, "Qiskit circuit and backend integration"),
    PackageCheck("IBM Aer", "qiskit_aer", False, "Qiskit Aer simulator integration"),
    PackageCheck("Google Quantum AI", "cirq", False, "Cirq circuit integration"),
    PackageCheck("Google qsim", "qsimcirq", False, "qsim-backed Cirq simulation"),
    PackageCheck("Open systems", "qutip", False, "QuTiP open-system experiments"),
    PackageCheck("Bosonic / cat-qubit", "dynamiqs", False, "Dynamiqs/JAX solver experiments"),
    PackageCheck("JAX backend", "jax", False, "JAX runtime used by Dynamiqs"),
]


def check_packages() -> list[PackageCheck]:
    results: list[PackageCheck] = []
    for check in CHECKS:
        results.append(
            PackageCheck(
                lane=check.lane,
                import_name=check.import_name,
                installed=importlib.util.find_spec(check.import_name) is not None,
                purpose=check.purpose,
            )
        )
    return results


def write_outputs(results: list[PackageCheck]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    JSON_PATH.write_text(json.dumps([asdict(r) for r in results], indent=2), encoding="utf-8")

    installed = sum(1 for result in results if result.installed)
    lines = [
        "# HQA Simulator Readiness",
        "",
        "## Purpose",
        "",
        "This report checks optional quantum simulator packages for HQA V2 integration work.",
        "",
        "HQA remains runnable without these packages. Missing packages mean the corresponding simulator lane is unavailable, not that HQA is broken.",
        "",
        "## Summary",
        "",
        f"- Optional packages checked: `{len(results)}`",
        f"- Installed: `{installed}`",
        f"- Missing: `{len(results) - installed}`",
        "",
        "| Lane | Import | Status | Purpose |",
        "|---|---|---:|---|",
    ]

    for result in results:
        status = "AVAILABLE" if result.installed else "MISSING"
        lines.append(f"| {result.lane} | `{result.import_name}` | {status} | {result.purpose} |")

    lines.extend(
        [
            "",
            "## Recommended Install Profiles",
            "",
            "- Core simulator lane: `pip install -r hqa_v2/integrations/requirements-core.txt`",
            "- Bosonic/cat-qubit lane: `pip install -r hqa_v2/integrations/requirements-bosonic.txt`",
            "- IBM Aer GPU lane: `pip install -r hqa_v2/integrations/requirements-ibm-gpu.txt`",
            "",
            "Use a dedicated virtual environment. Do not make these packages mandatory for the base HQA regression suite.",
            "",
            "## Boundary",
            "",
            "This readiness check validates Python package availability only. It does not validate physical quantum hardware, production QEC performance, or live backend access.",
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    results = check_packages()
    write_outputs(results)
    print(f"HQA simulator readiness written: {REPORT_PATH}")
    for result in results:
        status = "available" if result.installed else "missing"
        print(f"- {result.import_name}: {status}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

