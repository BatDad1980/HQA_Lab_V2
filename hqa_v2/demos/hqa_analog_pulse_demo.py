import json
import _bootstrap
from audit_logger import AuditLogger
from fabric_simulator import FabricSimulator
from topology_router import TopologyRouter
from pulse_translator import PulseTranslator

def run_analog_pulse_demo():
    audit_path = _bootstrap.log_path("analog_pulse_audit.json")
    report_path = _bootstrap.report_path("HQA_ANALOG_PULSE_SHAPING_REPORT.md")
    logger = AuditLogger(filepath=audit_path)
    logger.log("SYSTEM", "ANALOG_PULSE_DEMO_START", {"mode": "PHYSICS_LAYER"})
    
    fabric = FabricSimulator(logger, width=5, height=5)
    topology_map = fabric.get_topology_map()
    
    # Inject a degraded node near the route to force crosstalk mitigation
    fabric.inject_targeted_fault(1, 1, error_type="DEGRADED")
    fabric.nodes["Q_1_1"]["status"] = "DEGRADED" # Ensure status is set
    
    start_node = "Q_0_0"
    end_node = "Q_2_2"
    
    router = TopologyRouter(logger)
    current_path = router.reroute_circuit(topology_map, start_node, end_node)
    
    if current_path:
        translator = PulseTranslator(logger, fabric)
        # Generate the analog physical instructions instead of QASM
        manifest = translator.generate_hardware_instructions(current_path, dry_run=True)
        
        logger.log("SYSTEM", "MANIFEST_GENERATED", manifest["payload"])
        
    logger.log("SYSTEM", "ANALOG_PULSE_DEMO_COMPLETE", {"success": bool(current_path)})
    
    with open(report_path, "w") as f:
        f.write("# HQA Phase 8: Analog Microwave Pulse Shaping Report\n\n")
        f.write("This report demonstrates HQA translating proxy routing paths into analog pulse-envelope intents (DRAG/Gaussian-style) intended to model mitigation of local thermal crosstalk.\n\n")
        f.write("## JSON Audit Log\n```json\n")
        with open(audit_path, "r") as audit:
            f.write(audit.read())
        f.write("\n```\n")
    print("Evidence written to HQA_ANALOG_PULSE_SHAPING_REPORT.md")

if __name__ == "__main__":
    run_analog_pulse_demo()
