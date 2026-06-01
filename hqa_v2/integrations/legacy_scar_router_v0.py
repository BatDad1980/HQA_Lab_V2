"""Replay the useful routing primitive harvested from HQA V1.

This module rewrites the old Hippocampus/danger-gradient idea as a clean,
deterministic, vendor-neutral shadow artifact. It does not import the legacy
repo and it does not request live hardware authority.
"""

from __future__ import annotations

import heapq
import json
import math
import sys
from dataclasses import dataclass, field
from pathlib import Path


HQA_V2_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = HQA_V2_ROOT / "logs" / "legacy_scar_router_v0.json"
REPORT_PATH = HQA_V2_ROOT / "reports" / "HQA_LEGACY_SCAR_ROUTER_V0.md"


@dataclass
class Node:
    node_id: str
    x: int
    y: int
    status: str = "STABLE"
    error_type: str = "NONE"
    scar_risk: float = 0.0
    neighbors: set[str] = field(default_factory=set)


def node_id(x: int, y: int) -> str:
    return f"Q_{x}_{y}"


def build_sparse_grid(width: int, height: int, voids: set[str]) -> dict[str, Node]:
    nodes: dict[str, Node] = {}
    for y in range(height):
        for x in range(width):
            nid = node_id(x, y)
            if nid in voids:
                continue
            nodes[nid] = Node(node_id=nid, x=x, y=y)

    for node in nodes.values():
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            neighbor_id = node_id(node.x + dx, node.y + dy)
            if neighbor_id in nodes:
                node.neighbors.add(neighbor_id)
    return nodes


def apply_status(nodes: dict[str, Node], node: str, status: str, error_type: str = "GENERIC") -> None:
    nodes[node].status = status
    nodes[node].error_type = error_type


def radiate_scar_risk(nodes: dict[str, Node], source_id: str, radius: int = 1, phase_bias: bool = False) -> None:
    """Raise local advisory risk around a damaged node.

    A phase-flip source receives a stronger proximity penalty because the
    cat-qubit lane cares most about phase-flip propagation.
    """
    source = nodes[source_id]
    for node in nodes.values():
        distance = abs(node.x - source.x) + abs(node.y - source.y)
        if 0 < distance <= radius:
            node.scar_risk = max(node.scar_risk, 0.80 if phase_bias else 0.45)


def movement_cost(node: Node) -> float:
    if node.status in {"QUARANTINED", "SLEEPING", "VOID"}:
        return math.inf
    status_penalty = 4.0 if node.status == "DEGRADED" else 0.0
    return 1.0 + status_penalty + (node.scar_risk * 8.0)


def heuristic(a: Node, b: Node) -> float:
    return math.hypot(a.x - b.x, a.y - b.y)


def safest_path(nodes: dict[str, Node], start_id: str, end_id: str) -> tuple[list[str] | None, float]:
    frontier: list[tuple[float, str]] = [(0.0, start_id)]
    came_from: dict[str, str | None] = {start_id: None}
    cost_so_far: dict[str, float] = {start_id: 0.0}

    while frontier:
        _, current_id = heapq.heappop(frontier)
        if current_id == end_id:
            break

        for next_id in sorted(nodes[current_id].neighbors):
            step_cost = movement_cost(nodes[next_id])
            if step_cost == math.inf:
                continue

            new_cost = cost_so_far[current_id] + step_cost
            if next_id not in cost_so_far or new_cost < cost_so_far[next_id]:
                cost_so_far[next_id] = new_cost
                priority = new_cost + heuristic(nodes[next_id], nodes[end_id])
                heapq.heappush(frontier, (priority, next_id))
                came_from[next_id] = current_id

    if end_id not in came_from:
        return None, math.inf

    path: list[str] = []
    current: str | None = end_id
    while current is not None:
        path.append(current)
        current = came_from[current]
    path.reverse()
    return path, cost_so_far[end_id]


def run_scenarios() -> dict[str, object]:
    voids = {node_id(1, 0), node_id(3, 0), node_id(0, 2), node_id(4, 2), node_id(1, 4), node_id(3, 4)}

    scarred = build_sparse_grid(5, 5, voids)
    apply_status(scarred, "Q_2_2", "QUARANTINED", "GENERIC")
    apply_status(scarred, "Q_2_1", "DEGRADED", "GENERIC")
    apply_status(scarred, "Q_1_2", "SLEEPING", "CALIBRATION")
    radiate_scar_risk(scarred, "Q_2_2")
    scar_path, scar_cost = safest_path(scarred, "Q_0_1", "Q_4_3")

    generic = build_sparse_grid(5, 5, voids)
    apply_status(generic, "Q_2_2", "QUARANTINED", "GENERIC")
    radiate_scar_risk(generic, "Q_2_2", phase_bias=False)
    _, generic_cost = safest_path(generic, "Q_0_1", "Q_4_3")

    cat = build_sparse_grid(5, 5, voids)
    apply_status(cat, "Q_2_2", "QUARANTINED", "PHASE_FLIP")
    radiate_scar_risk(cat, "Q_2_2", phase_bias=True)
    _, cat_cost = safest_path(cat, "Q_0_1", "Q_4_3")

    blocked = build_sparse_grid(5, 5, voids)
    for blocked_id in ["Q_2_0", "Q_2_1", "Q_2_2", "Q_2_3", "Q_2_4"]:
        if blocked_id in blocked:
            apply_status(blocked, blocked_id, "QUARANTINED", "BARRIER")
    blocked_path, _ = safest_path(blocked, "Q_0_1", "Q_4_3")

    return {
        "schema_version": "hqa.legacy_scar_router.v0",
        "source_lineage": "HQA_V1 topological_memory.py, topology_mapper.py, sentinel_reflex.py",
        "execution_mode": "shadow_replay",
        "hardware_authority": False,
        "scenarios": {
            "scarred_sparse_grid": {
                "start": "Q_0_1",
                "end": "Q_4_3",
                "path": scar_path,
                "path_cost": None if scar_cost == math.inf else round(scar_cost, 3),
                "blocked_nodes": ["Q_2_2", "Q_1_2"],
                "action": "PROPOSE_REROUTE" if scar_path else "SAFE_HOLD",
            },
            "cat_phase_bias": {
                "generic_cost": None if generic_cost == math.inf else round(generic_cost, 3),
                "phase_flip_cost": None if cat_cost == math.inf else round(cat_cost, 3),
                "risk_bias_applied": cat_cost > generic_cost,
                "action": "ADVISORY_RISK_REWEIGHT",
            },
            "no_route_barrier": {
                "path": blocked_path,
                "action": "SAFE_HOLD" if blocked_path is None else "PROPOSE_REROUTE",
            },
        },
        "boundary": "This artifact ports a legacy routing pattern into deterministic shadow replay. It does not validate physical quantum hardware, alter pulses, or dispatch HAL commands.",
    }


def write_report(payload: dict[str, object]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    scenarios = payload["scenarios"]
    scar = scenarios["scarred_sparse_grid"]
    cat = scenarios["cat_phase_bias"]
    blocked = scenarios["no_route_barrier"]
    lines = [
        "# HQA Legacy Scar Router V0",
        "",
        "## Purpose",
        "",
        "This report records the first clean-lab harvest from the older HQA V1 line.",
        "",
        "The useful mechanism is the Hippocampus-style scar router: a pathfinder that treats quarantined nodes, sleeping calibration zones, structural voids, and nearby damage as routing constraints.",
        "",
        "## Results",
        "",
        "| Scenario | Result | Detail |",
        "|---|---:|---|",
        f"| Scarred sparse grid | `{scar['action']}` | Path `{scar['path']}` with cost `{scar['path_cost']}`. |",
        f"| Cat phase bias | `{cat['action']}` | Phase-flip cost `{cat['phase_flip_cost']}` vs generic cost `{cat['generic_cost']}`. |",
        f"| No-route barrier | `{blocked['action']}` | Barrier produced path `{blocked['path']}`. |",
        "",
        "## Harvested Pattern",
        "",
        "- V1 `Hippocampus` danger gradients become a vendor-neutral scar-risk field.",
        "- V1 sleep zones become temporary calibration holds.",
        "- V1 quarantined nodes become hard routing walls.",
        "- Cat-qubit phase-flip proximity gets a higher advisory cost than generic damage.",
        "",
        "## Boundary",
        "",
        payload["boundary"],
        "",
    ]
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    payload = run_scenarios()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    write_report(payload)
    print(f"HQA legacy scar router log written: {OUTPUT_PATH}")
    print(f"HQA legacy scar router report written: {REPORT_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
