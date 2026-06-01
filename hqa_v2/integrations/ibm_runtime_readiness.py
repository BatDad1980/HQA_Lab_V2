"""IBM Quantum runtime readiness check for HQA V2.

This script never reads credential files. It only checks environment variables
that the operator intentionally sets in the current shell.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


HQA_V2_ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = HQA_V2_ROOT / "reports" / "HQA_IBM_RUNTIME_READINESS.md"
JSON_PATH = HQA_V2_ROOT / "logs" / "ibm_runtime_readiness.json"


@dataclass
class RuntimeReadiness:
    package_available: bool
    token_env_present: bool
    instance_env_present: bool
    live_check_requested: bool
    live_check_performed: bool
    backend_count: int
    backend_names: list[str]
    error: str | None


def masked_present(value: str | None) -> bool:
    return bool(value and value.strip())


def run_live_backend_check(token: str, instance: str) -> tuple[list[str], str | None]:
    try:
        from qiskit_ibm_runtime import QiskitRuntimeService

        service = QiskitRuntimeService(token=token, instance=instance)
        backends = service.backends(operational=True)
        return [getattr(backend, "name", str(backend)) for backend in backends], None
    except Exception as exc:  # pragma: no cover - depends on external service.
        return [], f"{type(exc).__name__}: {exc}"


def collect_readiness(live: bool) -> RuntimeReadiness:
    package_available = importlib.util.find_spec("qiskit_ibm_runtime") is not None
    token = os.getenv("IBM_QUANTUM_TOKEN")
    instance = os.getenv("IBM_QUANTUM_INSTANCE_CRN")
    token_present = masked_present(token)
    instance_present = masked_present(instance)

    backend_names: list[str] = []
    error: str | None = None
    live_performed = False

    if live:
        if not package_available:
            error = "qiskit_ibm_runtime is not installed."
        elif not token_present or not instance_present:
            error = "IBM_QUANTUM_TOKEN and IBM_QUANTUM_INSTANCE_CRN must both be set."
        else:
            live_performed = True
            backend_names, error = run_live_backend_check(token or "", instance or "")

    return RuntimeReadiness(
        package_available=package_available,
        token_env_present=token_present,
        instance_env_present=instance_present,
        live_check_requested=live,
        live_check_performed=live_performed,
        backend_count=len(backend_names),
        backend_names=backend_names,
        error=error,
    )


def write_outputs(readiness: RuntimeReadiness) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    JSON_PATH.write_text(json.dumps(asdict(readiness), indent=2), encoding="utf-8")

    lines = [
        "# HQA IBM Runtime Readiness",
        "",
        "## Purpose",
        "",
        "This report checks whether HQA V2 can reach the optional IBM Quantum runtime lane.",
        "",
        "Credentials are never read from files, printed, committed, or packaged. This check only uses environment variables explicitly set in the active shell.",
        "",
        "## Status",
        "",
        f"- `qiskit_ibm_runtime` installed: `{readiness.package_available}`",
        f"- `IBM_QUANTUM_TOKEN` present: `{readiness.token_env_present}`",
        f"- `IBM_QUANTUM_INSTANCE_CRN` present: `{readiness.instance_env_present}`",
        f"- Live check requested: `{readiness.live_check_requested}`",
        f"- Live check performed: `{readiness.live_check_performed}`",
        f"- Operational backends returned: `{readiness.backend_count}`",
        "",
    ]

    if readiness.backend_names:
        lines.extend(["## Backends", ""])
        for name in readiness.backend_names:
            lines.append(f"- `{name}`")
        lines.append("")

    if readiness.error:
        lines.extend(["## Error", "", f"`{readiness.error}`", ""])

    lines.extend(
        [
            "## Usage",
            "",
            "```powershell",
            "$env:IBM_QUANTUM_TOKEN = \"<token>\"",
            "$env:IBM_QUANTUM_INSTANCE_CRN = \"<instance-crn>\"",
            "python hqa_v2/integrations/ibm_runtime_readiness.py --live",
            "```",
            "",
            "## Boundary",
            "",
            "This readiness check validates optional runtime access only. It does not submit jobs, reserve hardware, validate production quantum behavior, or grant HQA live hardware authority.",
            "",
        ]
    )

    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Check optional IBM Quantum runtime readiness.")
    parser.add_argument("--live", action="store_true", help="List operational IBM backends using env credentials.")
    args = parser.parse_args()

    readiness = collect_readiness(live=args.live)
    write_outputs(readiness)
    print(f"HQA IBM runtime readiness written: {REPORT_PATH}")
    print(f"- qiskit_ibm_runtime installed: {readiness.package_available}")
    print(f"- IBM_QUANTUM_TOKEN present: {readiness.token_env_present}")
    print(f"- IBM_QUANTUM_INSTANCE_CRN present: {readiness.instance_env_present}")
    print(f"- live check performed: {readiness.live_check_performed}")
    print(f"- operational backends returned: {readiness.backend_count}")
    if readiness.error:
        print(f"- error: {readiness.error}")
    return 1 if args.live and readiness.error else 0


if __name__ == "__main__":
    sys.exit(main())
