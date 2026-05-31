import socket

class CryostatController:
    """
    Simulates the physical, classical hardware cooling the quantum chip.
    In a real system, this is a dilution refrigerator pumping liquid helium.
    Now acts as a true Hardware Abstraction Layer (HAL) with physical TCP/SCPI support.
    """
    def __init__(self, fabric, mode="simulation", host="127.0.0.1", port=5000):
        self.fabric = fabric
        self.mode = mode
        self.host = host
        self.port = port
        self.pumps_active = [[False, False], [False, False]]
        
    def activate_cryo_pump(self, qx, qy):
        """
        Dumps liquid helium into the specified quadrant to aggressively cool it.
        This forces the physical thermal noise back to baseline.
        """
        if not self.pumps_active[qy][qx]:
            self.pumps_active[qy][qx] = True
            
            if self.mode == "physical":
                self._send_scpi_command(f"SET:CRYO:PUMP:Q{qx}{qy} ON")
            else:
                print(f"[CLASSICAL HARDWARE - SIMULATION] Alert: Activating Emergency Cryo-Pumps in Quadrant ({qx}, {qy})")
            
            # Physically cool the fabric in the simulation model
            self.fabric.apply_cooling(qx, qy)
            
            if self.mode != "physical":
                print(f"[CLASSICAL HARDWARE - SIMULATION] Quadrant ({qx}, {qy}) temperature stabilized to baseline.")

    def _send_scpi_command(self, command_string):
        """
        Opens a TCP socket, sends the SCPI string to the physical cryostat, and waits for ACK.
        """
        print(f"[HAL NETWORK] Transmitting to Cryostat {self.host}:{self.port} -> {command_string}")
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(2.0)
                s.connect((self.host, self.port))
                s.sendall((command_string + "\n").encode('utf-8'))
                
                # Wait for ACK from the physical hardware
                response = s.recv(1024).decode('utf-8').strip()
                print(f"[HAL NETWORK] Hardware Response: {response}")
        except Exception as e:
            print(f"[HAL NETWORK ERROR] Failed to communicate with physical hardware: {e}")

    def get_pump_status(self):
        return self.pumps_active
