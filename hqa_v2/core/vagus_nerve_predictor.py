class VagusNervePredictor:
    """
    A lightweight predictive module that tracks the 'velocity' of thermal degradation.
    Issues preemptive quarantine signals if a node is degrading too quickly.
    """
    def __init__(self, logger, fabric):
        self.logger = logger
        self.fabric = fabric
        self.history = {} # Tracks previous coherence states {node_id: [c1, c2, c3]}

    def analyze_drift_momentum(self):
        preemptive_signals = []
        
        for node_id, data in self.fabric.nodes.items():
            if data["status"] != "STABLE":
                continue
                
            current_coherence = data["coherence"]
            
            # Initialize history
            if node_id not in self.history:
                self.history[node_id] = []
            
            self.history[node_id].append(current_coherence)
            
            # Keep only the last 3 ticks of history
            if len(self.history[node_id]) > 3:
                self.history[node_id].pop(0)
                
            # Need at least 2 points to calculate velocity
            if len(self.history[node_id]) >= 2:
                # Calculate velocity (change per tick)
                # Coherence drops mean negative velocity
                velocity = self.history[node_id][-1] - self.history[node_id][-2]
                
                # If coherence is dropping dangerously fast (e.g., > 0.2 per tick)
                if velocity < -0.2 and current_coherence > 0.4:
                    self.logger.log("VAGUS_NERVE", "PREEMPTIVE_QUARANTINE_ISSUED", {
                        "node": node_id, 
                        "velocity": round(velocity, 3),
                        "current_coherence": round(current_coherence, 3),
                        "prediction": "Failure imminent within 2 ticks."
                    })
                    preemptive_signals.append({"node": node_id, "action": "PREEMPTIVE_QUARANTINE"})
                    
        return preemptive_signals
