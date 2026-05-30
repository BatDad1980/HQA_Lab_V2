class VagusNerve:
    """
    Pillar 2: Systemic Autonomic Responses.
    Monitors the Sentinel Reflexes across the fabric. If a localized cluster of Sentinels
    suddenly experiences massive stress (high correction counts), the Vagus Nerve recognizes
    a systemic physical threat (e.g., thermal spike) and commands the classical hardware to intervene.
    """
    def __init__(self, fabric, classical_hardware, stress_threshold=15):
        self.fabric = fabric
        self.classical_hardware = classical_hardware
        
        # How many local corrections in a single tick constitute a "Systemic Threat" in a quadrant
        self.stress_threshold = stress_threshold
        
    def monitor_and_regulate(self, sentinels):
        """
        Called every tick to aggregate sentinel stress and trigger autonomic responses.
        """
        # Track total corrections in this tick per quadrant
        quadrant_stress = [[0, 0], [0, 0]]
        
        # Aggregate stress from all sentinels
        for s in sentinels:
            qx = 0 if s.x_start < self.fabric.width // 2 else 1
            qy = 0 if s.y_start < self.fabric.height // 2 else 1
            quadrant_stress[qy][qx] += getattr(s, 'last_tick_corrections', 0)
            
        # Analyze stress and trigger physical hardware if needed
        for qy in range(2):
            for qx in range(2):
                if quadrant_stress[qy][qx] > self.stress_threshold:
                    print(f"\n[VAGUS NERVE] CRITICAL: Systemic thermal stress detected in Quadrant ({qx}, {qy}). Stress level: {quadrant_stress[qy][qx]} hits/tick.")
                    print("[VAGUS NERVE] Triggering Autonomic Reflex. Commanding Classical Hardware to intervene.")
                    self.classical_hardware.activate_cryo_pump(qx, qy)
