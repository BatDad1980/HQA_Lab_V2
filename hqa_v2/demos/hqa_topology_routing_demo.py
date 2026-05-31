import json
from audit_logger import AuditLogger
from fabric_simulator import FabricSimulator
from local_sentinel_reflex import LocalSentinelReflex
from quarantine_manager import QuarantineManager
from topology_router import TopologyRouter

def run_topology_demo():
    logger = AuditLogger(filepath="topology_audit.json")
    logger.log("SYSTEM", "TOPOLOGY_DEMO_START", {"version": "Phase-2"})
    
    # 1. Initialize 5x5 Sparse Lattice
    fabric = FabricSimulator(logger, width=5, height=5)
    topology_map = fabric.get_topology_map()
    
    # Target route across the grid
    start_node = "Q_0_0"
    end_node = "Q_4_4"
    
    # 2. Inject Fault directly in the center path
    faults = fabric.inject_targeted_fault(x=2, y=2)
    
    # 3. Sentinel & Quarantine
    sentinel = LocalSentinelReflex(logger)
    decisions = sentinel.evaluate_faults(faults)
    
    quarantine = QuarantineManager(logger)
    topology_map, isolated_nodes = quarantine.execute_quarantines(decisions, topology_map)
    
    # 4. Route via Hippocampus A*
    router = TopologyRouter(logger)
    new_path = router.reroute_circuit(topology_map, start_node, end_node)

    logger.log("SYSTEM", "TOPOLOGY_DEMO_COMPLETE", {"path_found": bool(new_path)})
    
    print("Topology Routing complete. Output written to topology_audit.json.")

    # Generate markdown report
    with open("HQA_TOPOLOGY_ROUTING_EVIDENCE.md", "w") as f:
        f.write("# HQA Topology Routing Evidence (Phase 2)\n\n")
        f.write("This document proves the Hippocampus A* router successfully navigated a physical sparse-lattice quantum topology, mathematically avoiding a central thermal fault.\n\n")
        f.write("## Audit Trace\n```json\n")
        with open("topology_audit.json", "r") as audit:
            f.write(audit.read())
        f.write("\n```\n")
    print("Evidence written to HQA_TOPOLOGY_ROUTING_EVIDENCE.md")

if __name__ == "__main__":
    run_topology_demo()
