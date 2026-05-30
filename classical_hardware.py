class CryostatController:
    """
    Simulates the physical, classical hardware cooling the quantum chip.
    In a real system, this is a dilution refrigerator pumping liquid helium.
    """
    def __init__(self, fabric):
        self.fabric = fabric
        self.pumps_active = [[False, False], [False, False]]
        
    def activate_cryo_pump(self, qx, qy):
        """
        Dumps liquid helium into the specified quadrant to aggressively cool it.
        This forces the physical thermal noise back to baseline.
        """
        if not self.pumps_active[qy][qx]:
            self.pumps_active[qy][qx] = True
            print(f"[CLASSICAL HARDWARE] Alert: Activating Emergency Cryo-Pumps in Quadrant ({qx}, {qy})")
            
            # Physically cool the fabric
            self.fabric.apply_cooling(qx, qy)
            print(f"[CLASSICAL HARDWARE] Quadrant ({qx}, {qy}) temperature stabilized to baseline.")

    def get_pump_status(self):
        return self.pumps_active
