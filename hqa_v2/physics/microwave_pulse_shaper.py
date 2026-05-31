class MicrowavePulseShaper:
    """
    Translates abstract logical gates (from the routing path) into explicit
    analog microwave pulse schedules required for physical cryostat execution.
    """
    def __init__(self, logger, fabric):
        self.logger = logger
        self.fabric = fabric
        self.base_amplitude = 0.5 # Volts
        self.base_duration_ns = 20.0 # Nanoseconds

    def calculate_crosstalk_penalty(self, node_id):
        """Reduces pulse amplitude if neighboring nodes are thermally unstable."""
        penalty = 0.0
        if node_id in self.fabric.edges:
            for neighbor in self.fabric.edges[node_id]:
                if neighbor in self.fabric.nodes:
                    n_status = self.fabric.nodes[neighbor]["status"]
                    if n_status == "DEGRADED":
                        penalty += 0.05
                    elif n_status == "UNSTABLE" or n_status == "QUARANTINED":
                        penalty += 0.15
        return penalty

    def shape_pulses(self, circuit_path):
        """Generates the analog pulse schedule."""
        schedule = []
        time_offset_ns = 0.0
        
        for node in circuit_path:
            # Calculate crosstalk mitigation
            crosstalk_penalty = self.calculate_crosstalk_penalty(node)
            safe_amplitude = max(0.1, self.base_amplitude - crosstalk_penalty)
            
            # DRAG (Derivative Removal by Adiabatic Gate) for specific phase suppression
            pulse_type = "DRAG" if crosstalk_penalty > 0 else "GAUSSIAN"
            
            # Formulate the physical analog envelope
            envelope = {
                "target_node": node,
                "start_time_ns": time_offset_ns,
                "duration_ns": self.base_duration_ns,
                "envelope_type": pulse_type,
                "peak_amplitude_v": round(safe_amplitude, 3),
                "detuning_mhz": round(crosstalk_penalty * 10, 2) # Detune frequency if crosstalk is high
            }
            
            schedule.append(envelope)
            time_offset_ns += self.base_duration_ns
            
        self.logger.log("PULSE_SHAPER", "ANALOG_SCHEDULE_GENERATED", {"operations": len(schedule), "total_duration_ns": time_offset_ns})
        return schedule
