import random

class QECSyndromeDecoder:
    """
    Simulates a classical hardware decoder that runs a repetition code 
    check to identify phase-flip (Z) syndromes dynamically.
    """
    def __init__(self, logger, fabric):
        self.logger = logger
        self.fabric = fabric

    def decode_syndromes(self):
        """Scans the fabric's current physical state for errors."""
        detected_syndromes = []
        
        for node_id, data in self.fabric.nodes.items():
            # If the fabric simulator drifted the coherence down, the QEC catches it
            if data["coherence"] < 0.5 and data["status"] == "STABLE":
                # Cat qubits specifically suffer phase flips when coherence drops
                error_type = "PHASE_FLIP"
                detected_syndromes.append({"node": node_id, "error_type": error_type, "coherence": data["coherence"]})
                
        if detected_syndromes:
            self.logger.log("QEC_DECODER", "SYNDROMES_DETECTED", {"count": len(detected_syndromes), "syndromes": detected_syndromes})
            
        return detected_syndromes
