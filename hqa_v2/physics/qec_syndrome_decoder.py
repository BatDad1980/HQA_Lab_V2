class QECSyndromeDecoder:
    """Detection stage of HQA's immune-system fault response — not a matching decoder.

    By design, HQA treats faults the way a body treats infection: detect a degraded
    region, reroute around it, quarantine ("scar") it, and anticipate the next
    failure. That is a different paradigm from surface-code error correction, not a
    failed attempt at one. This module is the *detection* stage of that response: it
    flags any fabric node whose scalar ``coherence`` health metric falls below a
    fixed threshold and labels it a phase-flip signal for the control plane to act
    on (reroute / quarantine).

    It deliberately does NOT extract stabilizer syndromes, build a matching graph,
    apply a code distance, or run MWPM / union-find / belief propagation — those
    belong to the decoder paradigm HQA is not competing in. "Syndrome/decoder" here
    is the biological detection sense, not the QEC-matching sense.
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
