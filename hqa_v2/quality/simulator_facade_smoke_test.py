"""Smoke-test the HQA optional simulator facade."""

from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path


HQA_V2_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = HQA_V2_ROOT.parent
REPORT_PATH = HQA_V2_ROOT / "reports" / "HQA_SIMULATOR_FACADE_SMOKE.md"
JSON_PATH = HQA_V2_ROOT / "logs" / "simulator_facade_smoke.json"

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from hqa_v2.integrations.simulator_facade import SimulatorUnavailable, available_simulators, get_simulator


def run_backend(name: str) -> dict:
    try:
        simulator = get_simulator(name, shots=256)
        circuit = simulator.build_bell_circuit()
        result = simulator.run(circuit)
        total_shots = sum(result.result.values())
        return {
            "name": name,
            "available": True,
            "ran": total_shots == 256,
            "runtime_s": round(result.runtime_s, 6),
            "backend": result.backend,
            "counts": result.result,
            "boundary": result.boundary,
            "error": None,
        }
    except (SimulatorUnavailable, Exception) as exc:
        return {
            "name": name,
            "available": False,
            "ran": False,
            "runtime_s": 0.0,
            "backend": "unavailable",
            "counts": {},
            "boundary": "No simulator run performed.",
            "error": f"{type(exc).__name__}: {exc}",
        }


def write_outputs(results: list[dict]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    JSON_PATH.write_text(json.dumps({"availability": available_simulators(), "results": results}, indent=2), encoding="utf-8")

    passed = sum(1 for result in results if result["ran"])
    lines = [
        "# HQA Simulator Facade Smoke Test",
        "",
        "## Purpose",
        "",
        "This smoke test verifies the unified optional simulator facade for local Qiskit Aer and Cirq/qsim lanes.",
        "",
        "## Results",
        "",
        f"- Backends checked: `{len(results)}`",
        f"- Ran successfully: `{passed}`",
        "",
        "| Backend | Available | Ran | Runtime Seconds | Counts | Boundary |",
        "|---|---:|---:|---:|---|---|",
    ]
    for result in results:
        lines.append(
            f"| `{result['name']}` | `{result['available']}` | `{result['ran']}` | `{result['runtime_s']}` | `{result['counts']}` | {result['boundary']} |"
        )
    errors = [result for result in results if result["error"]]
    if errors:
        lines.extend(["", "## Errors", ""])
        for result in errors:
            lines.append(f"- `{result['name']}`: `{result['error']}`")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This facade runs local simulator checks only. It does not submit live backend jobs or grant HQA hardware control authority.",
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    results = [run_backend("qiskit_aer"), run_backend("cirq")]
    write_outputs(results)
    failed = [result for result in results if not result["ran"]]
    print(f"HQA simulator facade smoke written: {REPORT_PATH}")
    print(f"Passed {len(results) - len(failed)}/{len(results)} checks.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
