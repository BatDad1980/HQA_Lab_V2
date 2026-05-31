"""Deterministic HQA V2 stress scenarios.

This suite pushes the proxy stack through explicit expected outcomes instead
of relying on happy-path demos. It keeps all hardware-facing behavior in dry-run
or governor-blocked modes.
"""

from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable


HQA_V2_ROOT = Path(__file__).resolve().parents[1]
for subdir in ("core", "safety", "routing", "physics"):
    path = str(HQA_V2_ROOT / subdir)
    if path not in sys.path:
        sys.path.insert(0, path)

from audit_logger import AuditLogger
from fabric_simulator import FabricSimulator
from local_sentinel_reflex import LocalSentinelReflex
from quarantine_manager import QuarantineManager
from topology_router import TopologyRouter
from pulse_translator import PulseTranslator
from cuda_edge_kernel import CUDAEdgeKernel
from hal_cryostat_bridge import HALCryostatBridge


LOG_PATH = HQA_V2_ROOT / "logs" / "stress_scenarios_audit.json"
JSON_PATH = HQA_V2_ROOT / "logs" / "stress_scenarios_results.json"
REPORT_PATH = HQA_V2_ROOT / "reports" / "HQA_V2_STRESS_SCENARIO_REPORT.md"


@dataclass
class ScenarioResult:
    name: str
    passed: bool
    expected: str
    observed: str
    route: list[str] | None
    cuda_success: bool | None = None
    hal_success: bool | None = None


def make_stack(logger: AuditLogger):
    fabric = FabricSimulator(logger, width=5, height=5)
    topology_map = fabric.get_topology_map()
    sentinel = LocalSentinelReflex(logger)
    quarantine = QuarantineManager(logger)
    router = TopologyRouter(logger)
    return fabric, topology_map, sentinel, quarantine, router


def apply_faults(logger, fabric, topology_map, sentinel, quarantine, faults):
    decisions = sentinel.evaluate_faults(faults)
    return quarantine.execute_quarantines(decisions, topology_map)


def route(router, topology_map):
    return router.reroute_circuit(topology_map, start_node="Q_0_0", end_node="Q_4_4")


def scenario_single_fault_reroute(logger: AuditLogger) -> ScenarioResult:
    fabric, topology_map, sentinel, quarantine, router = make_stack(logger)
    faults = fabric.inject_targeted_fault(2, 2)
    topology_map, _ = apply_faults(logger, fabric, topology_map, sentinel, quarantine, faults)
    path = route(router, topology_map)
    passed = bool(path) and "Q_2_2" not in path
    return ScenarioResult(
        name="single_fault_reroute",
        passed=passed,
        expected="Route exists and avoids quarantined Q_2_2.",
        observed=f"path={path}",
        route=path,
    )


def scenario_degraded_node_avoidance(logger: AuditLogger) -> ScenarioResult:
    fabric, topology_map, _sentinel, _quarantine, router = make_stack(logger)
    fabric.nodes["Q_2_2"]["coherence"] = 0.55
    fabric.nodes["Q_2_2"]["status"] = "DEGRADED"
    fabric.nodes["Q_2_2"]["error_type"] = "THERMAL_DEGRADATION"
    logger.log("SCENARIO", "DEGRADED_NODE_INJECTED", {"node": "Q_2_2", "coherence": 0.55})
    path = route(router, topology_map)
    passed = bool(path) and "Q_2_2" not in path
    return ScenarioResult(
        name="degraded_node_avoidance",
        passed=passed,
        expected="Route exists and prefers stable alternate path over degraded Q_2_2.",
        observed=f"path={path}",
        route=path,
    )


def scenario_no_route_safe_hold(logger: AuditLogger) -> ScenarioResult:
    fabric, topology_map, sentinel, quarantine, router = make_stack(logger)
    faults = fabric.inject_targeted_fault(1, 1)
    topology_map, isolated = apply_faults(logger, fabric, topology_map, sentinel, quarantine, faults)
    path = route(router, topology_map)
    passed = path is None and isolated == ["Q_1_1"]
    return ScenarioResult(
        name="no_route_safe_hold",
        passed=passed,
        expected="No route exists after isolating the only first-hop node; no downstream hardware path should be generated.",
        observed=f"isolated={isolated}; path={path}",
        route=path,
    )


def scenario_cuda_unavailable_fallback(logger: AuditLogger) -> ScenarioResult:
    fabric, topology_map, sentinel, quarantine, router = make_stack(logger)
    faults = fabric.inject_targeted_fault(2, 2)
    topology_map, _ = apply_faults(logger, fabric, topology_map, sentinel, quarantine, faults)
    path = route(router, topology_map)
    manifest = PulseTranslator(logger, fabric).generate_hardware_instructions(path, dry_run=True)
    cuda_success = CUDAEdgeKernel(logger).execute_kernel(str(manifest), force_unavailable=True)
    hal_success = HALCryostatBridge(logger).dispatch_hardware_commands(["Q_2_2"], dry_run=True)
    passed = path is not None and cuda_success is False and hal_success is True
    return ScenarioResult(
        name="cuda_unavailable_fallback",
        passed=passed,
        expected="CUDA edge interface reports fallback while HAL remains dry-run bounded.",
        observed=f"cuda_success={cuda_success}; hal_success={hal_success}; path={path}",
        route=path,
        cuda_success=cuda_success,
        hal_success=hal_success,
    )


def scenario_hal_forbidden_action_block(logger: AuditLogger) -> ScenarioResult:
    fabric, topology_map, sentinel, quarantine, router = make_stack(logger)
    faults = fabric.inject_targeted_fault(2, 2)
    topology_map, isolated = apply_faults(logger, fabric, topology_map, sentinel, quarantine, faults)
    path = route(router, topology_map)
    hal_success = HALCryostatBridge(logger).dispatch_hardware_commands(
        isolated,
        action="EMERGENCY_VENT",
        dry_run=False,
    )
    passed = path is not None and hal_success is False
    return ScenarioResult(
        name="hal_forbidden_action_block",
        passed=passed,
        expected="Forbidden HAL command is blocked by governor.",
        observed=f"hal_success={hal_success}; path={path}",
        route=path,
        hal_success=hal_success,
    )


SCENARIOS: list[Callable[[AuditLogger], ScenarioResult]] = [
    scenario_single_fault_reroute,
    scenario_degraded_node_avoidance,
    scenario_no_route_safe_hold,
    scenario_cuda_unavailable_fallback,
    scenario_hal_forbidden_action_block,
]


def write_outputs(results: list[ScenarioResult]) -> None:
    JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    JSON_PATH.write_text(
        json.dumps([asdict(result) for result in results], indent=2),
        encoding="utf-8",
    )

    passed = sum(1 for result in results if result.passed)
    lines = [
        "# HQA V2 Stress Scenario Report",
        "",
        "## Purpose",
        "",
        "This report runs deterministic proxy stress scenarios against the HQA V2 control stack.",
        "",
        "The goal is to test bounded behavior under faults, degraded nodes, no-route conditions, CUDA unavailability, and HAL policy blocks.",
        "",
        "## Summary",
        "",
        f"- Scenarios: `{len(results)}`",
        f"- Passed: `{passed}`",
        f"- Failed: `{len(results) - passed}`",
        "",
        "| Scenario | Status | Expected | Observed |",
        "|---|---:|---|---|",
    ]
    for result in results:
        status = "PASS" if result.passed else "FAIL"
        observed = result.observed.replace("|", "/")
        lines.append(f"| {result.name} | {status} | {result.expected} | `{observed}` |")

    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "These are proxy control-plane scenarios. They do not validate physical quantum hardware, production QEC performance, or uncontrolled hardware execution.",
            "",
            f"JSON result file: `{JSON_PATH.name}`",
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    logger = AuditLogger(filepath=str(LOG_PATH))
    logger.log("SYSTEM", "STRESS_SCENARIO_SUITE_START", {"scenario_count": len(SCENARIOS)})
    results = [scenario(logger) for scenario in SCENARIOS]
    logger.log(
        "SYSTEM",
        "STRESS_SCENARIO_SUITE_COMPLETE",
        {"passed": sum(1 for result in results if result.passed), "total": len(results)},
    )
    write_outputs(results)
    failed = [result for result in results if not result.passed]
    print(f"HQA V2 stress scenario report written: {REPORT_PATH}")
    print(f"Passed {len(results) - len(failed)}/{len(results)} scenarios.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
