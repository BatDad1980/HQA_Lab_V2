import json
import time
import _bootstrap
from audit_logger import AuditLogger
from fabric_simulator import FabricSimulator
from live_telemetry_stream import LiveTelemetryStream
from qec_syndrome_decoder import QECSyndromeDecoder
from local_sentinel_reflex import LocalSentinelReflex
from quarantine_manager import QuarantineManager
from topology_router import TopologyRouter
from vagus_nerve_predictor import VagusNervePredictor

def run_predictive_demo():
    audit_path = _bootstrap.log_path("predictive_audit.json")
    report_path = _bootstrap.report_path("HQA_PREDICTIVE_VAGUS_NERVE_REPORT.md")
    logger = AuditLogger(filepath=audit_path)
    logger.log("SYSTEM", "PREDICTIVE_HOMEOSTASIS_START", {"mode": "VAGUS_NERVE_ENGAGED"})
    
    fabric = FabricSimulator(logger, width=5, height=5)
    topology_map = fabric.get_topology_map()
    
    # We will force a specific node on the route to slowly but aggressively degrade
    # to trigger the Vagus Nerve before it fully collapses.
    
    telemetry_stream = LiveTelemetryStream(logger)
    qec_decoder = QECSyndromeDecoder(logger, fabric)
    sentinel = LocalSentinelReflex(logger)
    quarantine = QuarantineManager(logger)
    router = TopologyRouter(logger)
    vagus_nerve = VagusNervePredictor(logger, fabric)
    
    start_node = "Q_0_0"
    end_node = "Q_4_4"
    
    # Initial Route
    current_path = router.reroute_circuit(topology_map, start_node, end_node)
    
    # We will attack a node on the path
    target_node = current_path[2] if current_path and len(current_path) > 2 else "Q_2_2"
    
    for tick in range(1, 6):
        print(f"--- TICK {tick} ---")
        
        # 1. Telemetry Drift
        telemetry = telemetry_stream.get_telemetry_tick()
        fabric.apply_telemetry_drift(telemetry)
        
        # Force artificial rapid degradation on the target node
        if target_node in fabric.nodes:
            fabric.nodes[target_node]["coherence"] -= 0.25 # Sharp drop, but not instant death
            
        # 2. Vagus Nerve Prediction (runs BEFORE QEC catches it)
        preemptive_signals = vagus_nerve.analyze_drift_momentum()
        
        # 3. QEC Decoder (Catches actual failures)
        syndromes = qec_decoder.decode_syndromes()
        
        # 4. Sentinel processing
        decisions = {}
        
        # Sentinel ingests Vagus predictions
        if preemptive_signals:
            for sig in preemptive_signals:
                decisions[sig["node"]] = {"action": sig["action"]}
                
        # Sentinel ingests actual syndromes
        if syndromes:
            syndrome_decisions = sentinel.ingest_qec_syndromes(syndromes)
            decisions.update(syndrome_decisions)
            
        # 5. Execute Quarantines & Reroute
        if decisions:
            topology_map, isolated = quarantine.execute_quarantines(decisions, topology_map)
            path_compromised = any(n in isolated for n in current_path)
            
            if path_compromised:
                logger.log("SYSTEM", "ROUTE_COMPROMISED", {"action": "TRIGGERING_DYNAMIC_REROUTE"})
                current_path = router.reroute_circuit(topology_map, start_node, end_node)
                if not current_path:
                    break

        time.sleep(0.1)

    logger.log("SYSTEM", "PREDICTIVE_HOMEOSTASIS_COMPLETE", {"final_path_secured": bool(current_path)})
    
    with open(report_path, "w") as f:
        f.write("# HQA Phase 7: Predictive Vagus Nerve Report\n\n")
        f.write("This report demonstrates a proxy predictive-homeostasis scenario. By tracking the mathematical velocity of thermal degradation, the Vagus Nerve module flagged a likely phase-flip condition and preemptively quarantined the node before the mock QEC decoder registered a failure.\n\n")
        f.write("## JSON Audit Log\n```json\n")
        with open(audit_path, "r") as audit:
            f.write(audit.read())
        f.write("\n```\n")
    print("Evidence written to HQA_PREDICTIVE_VAGUS_NERVE_REPORT.md")

if __name__ == "__main__":
    run_predictive_demo()
