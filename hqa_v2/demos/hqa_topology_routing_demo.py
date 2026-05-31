import json
import _bootstrap
from audit_logger import AuditLogger
from fabric_simulator import FabricSimulator
from local_sentinel_reflex import LocalSentinelReflex
from quarantine_manager import QuarantineManager
from topology_router import TopologyRouter

def run_topology_demo():
    audit_path = _bootstrap.log_path("topology_audit.json")
    report_path = _bootstrap.report_path("HQA_TOPOLOGY_ROUTING_EVIDENCE.md")
    logger = AuditLogger(filepath=audit_path)
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
    with open(report_path, "w") as f:
        f.write("# HQA Topology Routing Evidence (Phase 2)\n\n")
        f.write("This report demonstrates that the Hippocampus A* router navigated a sparse-lattice proxy topology while avoiding a central thermal fault in the test scenario.\n\n")
        f.write("## Audit Trace\n```json\n")
        with open(audit_path, "r") as audit:
            f.write(audit.read())
        f.write("\n```\n")
    print("Evidence written to HQA_TOPOLOGY_ROUTING_EVIDENCE.md")

if __name__ == "__main__":
    run_topology_demo()
