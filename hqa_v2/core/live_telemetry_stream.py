import random

class LiveTelemetryStream:
    """
    Simulates a hardware SCPI stream constantly reporting environmental 
    drift (like cryostat temperature fluctuations).
    """
    def __init__(self, logger):
        self.logger = logger
        self.base_temp_mk = 15.0 # 15 milliKelvin base
        self.tick_count = 0

    def get_telemetry_tick(self):
        self.tick_count += 1
        
        # Simulate standard gaussian noise drift
        drift = random.gauss(0, 0.5)
        self.base_temp_mk += drift
        
        # Occasionally simulate a thermal spike
        spike_detected = False
        spike_location = None
        if random.random() < 0.15: # 15% chance per tick of a local spike
            spike_detected = True
            spike_location = f"Q_{random.randint(0, 4)}_{random.randint(0, 4)}"
            self.base_temp_mk += random.uniform(2.0, 5.0)

        telemetry = {
            "tick": self.tick_count,
            "global_temp_mk": round(self.base_temp_mk, 2),
            "local_spike": spike_location
        }
        
        self.logger.log("TELEMETRY_STREAM", "SENSOR_READING", telemetry)
        return telemetry
