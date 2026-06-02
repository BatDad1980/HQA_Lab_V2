"""Patch Routing Prototype V0.

Global node-level routing hits a latency/workload wall as the fabric grows.
This prototype tests a bounded alternative: route across coarse patches first,
then reserve node-level routing for local patch interiors.
"""

from __future__ import annotations

import heapq
import json
import math
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


HQA_V2_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = HQA_V2_ROOT / "logs" / "patch_routing_prototype_v0.json"
REPORT_PATH = HQA_V2_ROOT / "reports" / "HQA_PATCH_ROUTING_PROTOTYPE_V0.md"


@dataclass(frozen=True)
class PatchRoutingScenario:
    scenario_id: str
    title: str
    width: int
    height: int
    patch_size: int
    blocked_patches: set[tuple[int, int]]
    degraded_patches: set[tuple[int, int]]
    expected_decision: str


@dataclass(frozen=True)
class PatchRoutingResult:
    scenario_id: str
    title: str
    grid_nodes: int
    patch_nodes: int
    global_work_units: int
    patch_work_units: int
    workload_reduction: float
    global_latency_estimate_ms: float
    patch_latency_estimate_ms: float
    patch_path: list[str] | None
    decision: str
    hardware_authority: bool


SCENARIOS = [
    PatchRoutingScenario(
        scenario_id="PR-001",
        title="150x150 rupture-threshold grid",
        width=150,
        height=150,
        patch_size=15,
        blocked_patches={(4, 4), (5, 4), (4, 5)},
        degraded_patches={(6, 4), (6, 5), (5, 6)},
        expected_decision="PATCH_ROUTE_AVAILABLE",
    ),
    PatchRoutingScenario(
        scenario_id="PR-002",
        title="300x300 large fabric",
        width=300,
        height=300,
        patch_size=15,
        blocked_patches={(8, 8), (9, 8), (8, 9), (9, 9), (10, 9)},
        degraded_patches={(10, 8), (11, 8), (10, 10), (11, 10)},
        expected_decision="PATCH_ROUTE_AVAILABLE",
    ),
    PatchRoutingScenario(
        scenario_id="PR-003",
        title="600x600 coarse fabric",
        width=600,
        height=600,
        patch_size=20,
        blocked_patches={(14, 14), (15, 14), (14, 15), (15, 15), (16, 15), (15, 16)},
        degraded_patches={(17, 15), (17, 16), (16, 17), (18, 16)},
        expected_decision="PATCH_ROUTE_AVAILABLE",
    ),
    PatchRoutingScenario(
        scenario_id="PR-004",
        title="Patch wall no-route hold",
        width=300,
        height=300,
        patch_size=15,
        blocked_patches={(10, y) for y in range(20)},
        degraded_patches=set(),
        expected_decision="SAFE_HOLD",
    ),
]


def patch_id(x: int, y: int) -> str:
    return f"P_{x}_{y}"


def parse_patch_id(value: str) -> tuple[int, int]:
    _, x, y = value.split("_")
    return int(x), int(y)


def patch_dimensions(width: int, height: int, patch_size: int) -> tuple[int, int]:
    return math.ceil(width / patch_size), math.ceil(height / patch_size)


def neighbors(node: tuple[int, int], max_x: int, max_y: int) -> list[tuple[int, int]]:
    x, y = node
    out: list[tuple[int, int]] = []
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nx, ny = x + dx, y + dy
        if 0 <= nx < max_x and 0 <= ny < max_y:
            out.append((nx, ny))
    return out


def route_patches(
    patch_w: int,
    patch_h: int,
    blocked: set[tuple[int, int]],
    degraded: set[tuple[int, int]],
    start: tuple[int, int],
    end: tuple[int, int],
) -> tuple[list[str] | None, int]:
    frontier: list[tuple[float, tuple[int, int]]] = [(0.0, start)]
    came_from: dict[tuple[int, int], tuple[int, int] | None] = {start: None}
    cost_so_far: dict[tuple[int, int], float] = {start: 0.0}
    expanded = 0

    while frontier:
        _, current = heapq.heappop(frontier)
        expanded += 1
        if current == end:
            break

        for next_node in neighbors(current, patch_w, patch_h):
            if next_node in blocked:
                continue
            step_cost = 6.0 if next_node in degraded else 1.0
            new_cost = cost_so_far[current] + step_cost
            if next_node not in cost_so_far or new_cost < cost_so_far[next_node]:
                cost_so_far[next_node] = new_cost
                heuristic = abs(end[0] - next_node[0]) + abs(end[1] - next_node[1])
                heapq.heappush(frontier, (new_cost + heuristic, next_node))
                came_from[next_node] = current

    if end not in came_from:
        return None, expanded

    path: list[tuple[int, int]] = []
    current: tuple[int, int] | None = end
    while current is not None:
        path.append(current)
        current = came_from[current]
    path.reverse()
    return [patch_id(x, y) for x, y in path], expanded


def estimate_global_latency_ms(global_work_units: int) -> float:
    # Calibrated to the observed 150x150 global A* stress result: 22,500 nodes -> ~205 ms.
    return round((global_work_units / 22_500.0) * 205.0, 3)


def estimate_patch_latency_ms(patch_work_units: int, patch_size: int, path_len: int) -> float:
    # Patch planning plus bounded local work along the selected path.
    local_work = path_len * patch_size * 0.35
    return round(((patch_work_units + local_work) / 22_500.0) * 205.0, 3)


def run_scenario(scenario: PatchRoutingScenario) -> PatchRoutingResult:
    patch_w, patch_h = patch_dimensions(scenario.width, scenario.height, scenario.patch_size)
    start = (0, 0)
    end = (patch_w - 1, patch_h - 1)
    path, expanded = route_patches(patch_w, patch_h, scenario.blocked_patches, scenario.degraded_patches, start, end)
    grid_nodes = scenario.width * scenario.height
    patch_nodes = patch_w * patch_h
    global_work_units = grid_nodes
    patch_work_units = expanded
    path_len = len(path or [])
    global_latency = estimate_global_latency_ms(global_work_units)
    patch_latency = estimate_patch_latency_ms(patch_work_units, scenario.patch_size, path_len)
    decision = "PATCH_ROUTE_AVAILABLE" if path else "SAFE_HOLD"
    reduction = global_work_units / max(1, patch_work_units)
    return PatchRoutingResult(
        scenario_id=scenario.scenario_id,
        title=scenario.title,
        grid_nodes=grid_nodes,
        patch_nodes=patch_nodes,
        global_work_units=global_work_units,
        patch_work_units=patch_work_units,
        workload_reduction=round(reduction, 3),
        global_latency_estimate_ms=global_latency,
        patch_latency_estimate_ms=patch_latency,
        patch_path=path,
        decision=decision,
        hardware_authority=False,
    )


def run_prototype() -> dict[str, object]:
    results = [run_scenario(scenario) for scenario in SCENARIOS]
    return {
        "schema_version": "hqa.patch_routing_prototype.v0",
        "execution_mode": "shadow_routing_prototype",
        "hardware_authority": False,
        "scenario_count": len(results),
        "results": [asdict(result) for result in results],
        "expected": [
            {
                "scenario_id": scenario.scenario_id,
                "expected_decision": scenario.expected_decision,
            }
            for scenario in SCENARIOS
        ],
        "boundary": "Patch routing is a shadow planning prototype only. It does not validate physical quantum hardware, alter topology, change pulses, or dispatch HAL actions.",
    }


def write_report(payload: dict[str, object]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# HQA Patch Routing Prototype V0",
        "",
        "## Purpose",
        "",
        "This report tests a patch-level routing prototype for fabrics where global node-level A* approaches the feedback budget.",
        "",
        "The prototype routes across coarse regions first and preserves safe-hold behavior when a patch wall blocks the fabric.",
        "",
        "## Results",
        "",
        "| Scenario | Grid Nodes | Patch Nodes | Workload Reduction | Global Latency Est. | Patch Latency Est. | Decision |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for result in payload["results"]:
        lines.append(
            f"| `{result['scenario_id']}` {result['title']} | `{result['grid_nodes']}` | `{result['patch_nodes']}` | `{result['workload_reduction']}` | `{result['global_latency_estimate_ms']}` | `{result['patch_latency_estimate_ms']}` | `{result['decision']}` |"
        )
    lines.extend(["", "## Boundary", "", payload["boundary"], ""])
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    payload = run_prototype()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    write_report(payload)
    print(f"HQA patch routing prototype written: {OUTPUT_PATH}")
    print(f"HQA patch routing report written: {REPORT_PATH}")
    for result in payload["results"]:
        print(
            f"- {result['scenario_id']}: {result['decision']}, "
            f"{result['workload_reduction']}x workload reduction"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
