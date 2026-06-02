"""Run the HQA V2 safe demo/regression set and summarize results."""

from __future__ import annotations

import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
HQA_V2_ROOT = REPO_ROOT / "hqa_v2"
REPORT_PATH = HQA_V2_ROOT / "reports" / "HQA_V2_REGRESSION_SUMMARY.md"


@dataclass
class RunResult:
    name: str
    command: list[str]
    returncode: int
    seconds: float
    stdout_tail: str
    stderr_tail: str


SAFE_COMMANDS = [
    ("HAL safety", ["python", "hqa_v2/demos/hqa_hal_safety_demo.py"]),
    ("Topology routing", ["python", "hqa_v2/demos/hqa_topology_routing_demo.py"]),
    ("Live telemetry", ["python", "hqa_v2/demos/hqa_live_control_loop_demo.py"]),
    ("Predictive homeostasis", ["python", "hqa_v2/demos/hqa_predictive_homeostasis_demo.py"]),
    ("CR routing", ["python", "hqa_v2/demos/hqa_cr_routing_demo.py"]),
    ("Analog pulse shaping", ["python", "hqa_v2/demos/hqa_analog_pulse_demo.py"]),
    ("Cat-qubit proxy", ["python", "hqa_v2/demos/alice_and_bob_cat_qubit_demo.py"]),
    ("Simulator readiness", ["python", "hqa_v2/integrations/simulator_readiness.py"]),
    ("IBM runtime dry readiness", ["python", "hqa_v2/integrations/ibm_runtime_readiness.py"]),
    ("Simulator adapter smoke", ["python", "hqa_v2/quality/simulator_adapter_smoke_test.py"]),
    ("Simulator facade smoke", ["python", "hqa_v2/quality/simulator_facade_smoke_test.py"]),
    ("Qiskit cascade observer", ["python", "hqa_v2/integrations/qiskit_cascade_observer.py"]),
    ("Qiskit Aer cascade noise probe", ["python", "hqa_v2/integrations/qiskit_aer_cascade_noise_probe.py"]),
    ("Qiskit Aer cascade gate", ["python", "hqa_v2/quality/qiskit_aer_cascade_gate.py"]),
    ("HQA risk field", ["python", "hqa_v2/integrations/hqa_risk_field_v0.py"]),
    ("HQA risk field gate", ["python", "hqa_v2/quality/hqa_risk_field_gate.py"]),
    ("Shadow adaptive proposal", ["python", "hqa_v2/integrations/shadow_adaptive_proposal_v0.py"]),
    ("Shadow adaptive proposal gate", ["python", "hqa_v2/quality/shadow_adaptive_proposal_gate.py"]),
    ("Simulator stress schedule", ["python", "hqa_v2/integrations/simulator_stress_schedule_v0.py"]),
    ("Simulator stress schedule gate", ["python", "hqa_v2/quality/simulator_stress_schedule_gate.py"]),
    ("Environment profile library", ["python", "hqa_v2/integrations/environment_profile_library_v0.py"]),
    ("Environment profile library gate", ["python", "hqa_v2/quality/environment_profile_library_gate.py"]),
    ("Cat cascade proxy", ["python", "hqa_v2/integrations/cat_cascade_proxy.py"]),
    ("Cat solver contract", ["python", "hqa_v2/integrations/cat_solver_contract_v0.py"]),
    ("Cat solver contract gate", ["python", "hqa_v2/quality/cat_solver_contract_gate.py"]),
    ("External quantum trace intake", ["python", "hqa_v2/integrations/external_quantum_trace_intake_v0.py"]),
    ("External quantum trace intake gate", ["python", "hqa_v2/quality/external_quantum_trace_intake_gate.py"]),
    ("Topology compensation profiles", ["python", "hqa_v2/integrations/topology_compensation_profiles_v0.py"]),
    ("Topology compensation profiles gate", ["python", "hqa_v2/quality/topology_compensation_profiles_gate.py"]),
    ("Dual vendor test matrix", ["python", "hqa_v2/integrations/dual_vendor_test_matrix_v0.py"]),
    ("Dual vendor test matrix gate", ["python", "hqa_v2/quality/dual_vendor_test_matrix_gate.py"]),
    ("Legacy scar router", ["python", "hqa_v2/integrations/legacy_scar_router_v0.py"]),
    ("Legacy scar router gate", ["python", "hqa_v2/quality/legacy_scar_router_gate.py"]),
    ("Legacy autonomic stress regulator", ["python", "hqa_v2/integrations/legacy_autonomic_stress_regulator_v0.py"]),
    ("Legacy autonomic stress regulator gate", ["python", "hqa_v2/quality/legacy_autonomic_stress_regulator_gate.py"]),
    ("HQA mud run", ["python", "hqa_v2/integrations/hqa_mud_run_v0.py"]),
    ("HQA mud run gate", ["python", "hqa_v2/quality/hqa_mud_run_gate.py"]),
    ("Cognitive advisory contract", ["python", "hqa_v2/integrations/cognitive_advisory_contract_v0.py"]),
    ("Cognitive advisory contract gate", ["python", "hqa_v2/quality/cognitive_advisory_contract_gate.py"]),
    ("HQA intervention gate", ["python", "hqa_v2/integrations/hqa_intervention_gate_v0.py"]),
    ("HQA intervention gate quality", ["python", "hqa_v2/quality/hqa_intervention_gate_quality.py"]),
    ("Telemetry compression gate", ["python", "hqa_v2/integrations/telemetry_compression_gate_v0.py"]),
    ("Telemetry compression gate quality", ["python", "hqa_v2/quality/telemetry_compression_gate_quality.py"]),
    ("Patch routing prototype", ["python", "hqa_v2/integrations/patch_routing_prototype_v0.py"]),
    ("Patch routing prototype quality", ["python", "hqa_v2/quality/patch_routing_prototype_quality.py"]),
    ("Provider normalization matrix", ["python", "hqa_v2/integrations/provider_normalization_matrix_v0.py"]),
    ("Provider normalization matrix gate", ["python", "hqa_v2/quality/provider_normalization_matrix_gate.py"]),
    ("Provider replay harness", ["python", "hqa_v2/integrations/provider_replay_harness_v0.py"]),
    ("Provider replay harness gate", ["python", "hqa_v2/quality/provider_replay_harness_gate.py"]),
    ("Evidence dashboard", ["python", "hqa_v2/demos/build_evidence_dashboard_v0.py"]),
    ("Evidence dashboard gate", ["python", "hqa_v2/quality/evidence_dashboard_gate.py"]),
    ("Schema contract smoke", ["python", "hqa_v2/quality/schema_contract_smoke_test.py"]),
    ("Vendor shadow packet", ["python", "hqa_v2/package/build_vendor_shadow_packet.py"]),
    ("Vendor shadow packet validation", ["python", "hqa_v2/quality/vendor_shadow_packet_validation.py"]),
    ("Stress harness", ["python", "hqa_v2/demos/hqa_stress_harness.py"]),
    ("Deterministic stress scenarios", ["python", "hqa_v2/quality/hqa_v2_stress_scenarios.py"]),
    ("Integrated loop", ["python", "hqa_v2/demos/hqa_v2_integrated_control_loop.py"]),
    ("Claim boundary smoke", ["python", "hqa_v2/quality/claim_boundary_smoke_test.py"]),
]


def tail(text: str, lines: int = 8) -> str:
    split = text.strip().splitlines()
    return "\n".join(split[-lines:])


def run_command(name: str, command: list[str]) -> RunResult:
    started = time.perf_counter()
    completed = subprocess.run(
        command,
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
    )
    elapsed = time.perf_counter() - started
    return RunResult(
        name=name,
        command=command,
        returncode=completed.returncode,
        seconds=elapsed,
        stdout_tail=tail(completed.stdout),
        stderr_tail=tail(completed.stderr),
    )


def write_report(results: list[RunResult]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    passed = sum(1 for result in results if result.returncode == 0)
    failed = len(results) - passed

    lines = [
        "# HQA V2 Regression Summary",
        "",
        "## Purpose",
        "",
        "This report summarizes the safe HQA V2 proxy demo/regression set.",
        "",
        "It verifies that the demos run from a clean repository root and that active text artifacts pass the claim-boundary smoke test.",
        "",
        "## Results",
        "",
        f"- Commands run: `{len(results)}`",
        f"- Passed: `{passed}`",
        f"- Failed: `{failed}`",
        "",
        "| Check | Status | Seconds | Command |",
        "|---|---:|---:|---|",
    ]

    for result in results:
        status = "PASS" if result.returncode == 0 else "FAIL"
        command = " ".join(result.command)
        lines.append(f"| {result.name} | {status} | {result.seconds:.3f} | `{command}` |")

    lines.extend(["", "## Failure Details", ""])
    failures = [result for result in results if result.returncode != 0]
    if not failures:
        lines.append("No failures.")
    else:
        for result in failures:
            lines.extend(
                [
                    f"### {result.name}",
                    "",
                    "STDOUT:",
                    "",
                    "```text",
                    result.stdout_tail or "(empty)",
                    "```",
                    "",
                    "STDERR:",
                    "",
                    "```text",
                    result.stderr_tail or "(empty)",
                    "```",
                    "",
                ]
            )

    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This regression suite validates proxy control-flow behavior only. It does not claim physical quantum validation, production QEC performance, or uncontrolled hardware execution.",
            "",
        ]
    )

    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    results = [run_command(name, command) for name, command in SAFE_COMMANDS]
    write_report(results)
    failed = [result for result in results if result.returncode != 0]
    print(f"HQA V2 regression summary written: {REPORT_PATH}")
    print(f"Passed {len(results) - len(failed)}/{len(results)} checks.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
