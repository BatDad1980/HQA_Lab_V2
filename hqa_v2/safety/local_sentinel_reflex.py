class LocalSentinelReflex:
    def __init__(self, logger):
        self.logger = logger

    def ingest_qec_syndromes(self, syndromes):
        """
        Real-time response to dynamic syndromes detected by the QEC Decoder.
        Triggers emergency quarantine if coherence drops below critical limits.
        """
        quarantine_decisions = {}
        for syn in syndromes:
            if syn["coherence"] < 0.4:
                self.logger.log("SENTINEL", "EMERGENCY_QUENCH_TRIGGERED", {"node": syn["node"], "reason": "live_syndrome_detection"})
                quarantine_decisions[syn["node"]] = {"action": "QUARANTINE"}
        return quarantine_decisions

    def evaluate_faults(self, faults, conflicting_signal=False):
        decisions = {}
        
        if conflicting_signal:
            self.logger.log("SENTINEL", "CONFLICT_DETECTED", {"signal": "external_override", "action": "ignored_in_favor_of_local_reflex"})

        for f in faults:
            node = f["node"]
            coh = f["coherence"]
            if coh < 0.4:
                decisions[node] = "QUARANTINE_REQUIRED"
                self.logger.log("SENTINEL", "QUENCH_DECISION", {"node": node, "reason": "coherence_critical", "coherence": coh})
            elif coh < 0.7:
                decisions[node] = "DEGRADED_TOLERATED"
                self.logger.log("SENTINEL", "THROTTLE_DECISION", {"node": node, "reason": "coherence_degraded", "coherence": coh})
            else:
                decisions[node] = "SAFE"
                
        return decisions
