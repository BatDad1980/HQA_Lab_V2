import json
import _bootstrap
from audit_logger import AuditLogger
from fabric_simulator import FabricSimulator
from cross_resonance_scheduler import CrossResonanceScheduler

def run_cr_routing_demo():
    audit_path = _bootstrap.log_path("cr_routing_audit.json")
    report_path = _bootstrap.report_path("HQA_CR_GATE_ROUTING_REPORT.md")
    logger = AuditLogger(filepath=audit_path)
    logger.log("SYSTEM", "CR_ROUTING_DEMO_START", {"mode": "TWO_QUBIT_ENTANGLEMENT"})
    
    fabric = FabricSimulator(logger, width=5, height=5)
    
    # Fault the fabric so the scheduler must hunt for a pristine edge, without
    # stranding either logical qubit: kill the central coupler and degrade one hub.
    fabric.inject_targeted_fault(2, 2, error_type="QUARANTINED")
    fabric.nodes["Q_2_2"]["status"] = "QUARANTINED"
    fabric.inject_targeted_fault(3, 1, error_type="DEGRADED")
    fabric.nodes["Q_3_1"]["status"] = "DEGRADED"
    
    topology_map = fabric.get_topology_map()
    
    logical_state_a = "Q_0_0"
    logical_state_b = "Q_4_4"
    
    scheduler = CrossResonanceScheduler(logger, topology_map)
    path_a, path_b = scheduler.schedule_two_qubit_gate(logical_state_a, logical_state_b)
    
    logger.log("SYSTEM", "CR_ROUTING_DEMO_COMPLETE", {"success": bool(path_a and path_b)})
    
    with open(report_path, "w") as f:
        f.write("# HQA Phase 9: Cross-Resonance Gate Routing Report\n\n")
        f.write("This report demonstrates HQA operating beyond single-path routing in a proxy scenario. The scheduler scans the sparse-lattice for a usable physical edge and asks the Hippocampus router to place two logical states near that pair for a simulated CR-gate workflow.\n\n")
        f.write("## JSON Audit Log\n```json\n")
        with open(audit_path, "r") as audit:
            f.write(audit.read())
        f.write("\n```\n")
    print("Evidence written to HQA_CR_GATE_ROUTING_REPORT.md")

if __name__ == "__main__":
    run_cr_routing_demo()
