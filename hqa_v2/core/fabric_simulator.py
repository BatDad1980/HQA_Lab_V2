from topology_mapper import TopologyMapper
import random

class FabricSimulator:
    def __init__(self, logger, width=5, height=5):
        self.logger = logger
        self.mapper = TopologyMapper(width=width, height=height)
        self.nodes = self.mapper.nodes
        self.edges = self.mapper.edges
            
        self.logger.log("FABRIC_SIMULATOR", "INITIALIZE", {
            "nodes": len(self.nodes),
            "topology": "SPARSE_LATTICE",
            "grid_size": f"{width}x{height}"
        })

    def inject_targeted_fault(self, x, y, error_type="THERMAL_DEGRADATION"):
        """Injects a catastrophic fault at a specific physical coordinate."""
        target = f"Q_{x}_{y}"
        if target in self.nodes:
            self.nodes[target]["coherence"] = 0.1
            self.nodes[target]["status"] = "UNSTABLE"
            self.nodes[target]["error_type"] = error_type
            self.logger.log("FABRIC_SIMULATOR", "FAULT_INJECTED", {"node": target, "coherence": 0.1, "error_type": error_type})
            return [{"node": target, "coherence": 0.1, "status": "UNSTABLE", "error_type": error_type}]
        return []

    def inject_asymmetric_cat_qubit_stress(self):
        """
        Specific to Alice & Bob integration.
        Bit-flips (X-errors) are exponentially suppressed by hardware.
        Injects purely Phase-Flips (Z-errors) to test proxy routing logic.
        """
        self.logger.log("FABRIC_SIMULATOR", "CAT_QUBIT_MODE_ENGAGED", {"bit_flip_suppression": "EXPONENTIAL", "phase_flip_vulnerability": "EXPOSED"})
        faults = []
        
        # Inject purely Z-errors (phase flips)
        faults.extend(self.inject_targeted_fault(1, 1, error_type="PHASE_FLIP"))
        faults.extend(self.inject_targeted_fault(3, 3, error_type="PHASE_FLIP"))
        
        self.logger.log("FABRIC_SIMULATOR", "ASYMMETRIC_STRESS_INJECTED", {"faults": faults})
        return faults

    def inject_stress(self):
        """Injects multiple faults and degraded states."""
        faults = []
        # Target 2-3 nodes for stress
        targets = random.sample(list(self.nodes.keys()), random.randint(2, 3))
        
        for t in targets:
            # 50% chance of dead (<0.4), 50% chance of degraded (0.4 - 0.7)
            coherence = round(random.uniform(0.1, 0.7), 2)
            self.nodes[t]["coherence"] = coherence
            self.nodes[t]["status"] = "DEGRADED" if coherence >= 0.4 else "UNSTABLE"
            faults.append({"node": t, "coherence": coherence, "status": self.nodes[t]["status"]})

        self.logger.log("FABRIC_SIMULATOR", "STRESS_INJECTED", {"faults": faults})
        return faults
            
    def apply_telemetry_drift(self, telemetry):
        """
        Dynamically adjusts the fabric's physical state based on live telemetry.
        If a local thermal spike is detected, the coherence of that node collapses.
        """
        spike = telemetry.get("local_spike")
        if spike and spike in self.nodes:
            # Thermal spike causes immediate coherence collapse
            self.nodes[spike]["coherence"] = max(0.0, self.nodes[spike]["coherence"] - 0.6)
            self.logger.log("FABRIC_SIMULATOR", "THERMAL_SPIKE_IMPACT", {"node": spike, "new_coherence": self.nodes[spike]["coherence"]})
        
        # General background drift (slowly degrades everything slightly)
        for node_id, data in self.nodes.items():
            if data["status"] == "STABLE":
                data["coherence"] -= 0.01
                if data["coherence"] < 0.0: data["coherence"] = 0.0

    def get_topology_map(self):
        return {"nodes": self.nodes, "edges": self.edges}
