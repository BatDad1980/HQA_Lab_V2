import random
import copy

class QubitFabric:
    def __init__(self, width=20, height=20, noise_rate=0.02, cascade_threshold=3, topology_mask=None):
        self.width = width
        self.height = height
        self.noise_rate = noise_rate
        self.cascade_threshold = cascade_threshold
        
        # 0 = Healthy, >0 = Age of the error (ticks since it appeared)
        # -1 = Quarantined (Dead qubit)
        # -2 = Physical Void (No silicon exists here due to topology)
        self.grid = [[0 for _ in range(width)] for _ in range(height)]
        
        # Apply physical topology mask if provided
        if topology_mask:
            for y in range(height):
                for x in range(width):
                    if not topology_mask[y][x]:
                        self.grid[y][x] = -2 # Physical void
                        
        # Track permanently degraded nodes (hardware faults)
        self.faults = set()
        
        # Track permanently severed/quarantined nodes
        self.quarantined_nodes = set()
        
        # Track the "logical weight" or computational load of each node. Default is 1.0.
        self.logical_weights = [[1.0 if self.grid[y][x] != -2 else 0.0 for x in range(width)] for y in range(height)]
        
        # Localized thermal profiles: quadrant-based noise multipliers (Default 1.0)
        # Structure: [[Top-Left, Top-Right], [Bottom-Left, Bottom-Right]]
        self.thermal_zones = [[1.0, 1.0], [1.0, 1.0]]
        
        # Track sleeping nodes (intentionally decohered for calibration)
        self.sleep_zones = set()
        
    def quarantine_node(self, x, y):
        """
        Phase 4: Sentinel Quarantine Protocol.
        Permanently severs a dead node from the grid and redistributes its logical weight
        to the surrounding healthy lattice.
        """
        if 0 <= x < self.width and 0 <= y < self.height and (x, y) not in self.quarantined_nodes:
            self.quarantined_nodes.add((x, y))
            self.grid[y][x] = -1 # Physically isolated
            
            # Redistribute its logical weight to healthy neighbors
            weight_to_distribute = self.logical_weights[y][x]
            self.logical_weights[y][x] = 0.0 # Node is dead
            
            neighbors = []
            for dy in [-1, 0, 1]:
                for dx in [-1, 0, 1]:
                    if dx == 0 and dy == 0: continue
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.width and 0 <= ny < self.height:
                        if (nx, ny) not in self.quarantined_nodes:
                            neighbors.append((nx, ny))
            
            if neighbors:
                share = weight_to_distribute / len(neighbors)
                for nx, ny in neighbors:
                    self.logical_weights[ny][nx] += share

    def enter_sleep(self, x, y):
        """Intentionally decoheres a node and pauses its physics."""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.sleep_zones.add((x, y))
            self.grid[y][x] = 0 # Flush the noise
            
    def awaken(self, x, y):
        """Brings a node back online."""
        if (x, y) in self.sleep_zones:
            self.sleep_zones.remove((x, y))
    def inject_hardware_faults(self, num_faults=5, cluster_zones=0, cluster_radius=3):
        """Simulates physical degradation where certain qubits are always noisy.
        Can inject isolated faults or dense clusters representing thermal hot spots."""
        # 1. Isolated faults
        for _ in range(num_faults):
            x, y = random.randint(0, self.width-1), random.randint(0, self.height-1)
            self.faults.add((x, y))
            self.grid[y][x] = 1
            
        # 2. Clustered faults (Hot zones)
        for _ in range(cluster_zones):
            cx, cy = random.randint(0, self.width-1), random.randint(0, self.height-1)
            for dy in range(-cluster_radius, cluster_radius+1):
                for dx in range(-cluster_radius, cluster_radius+1):
                    # Create a rough circle
                    if dx*dx + dy*dy <= cluster_radius*cluster_radius:
                        x, y = cx + dx, cy + dy
                        if 0 <= x < self.width and 0 <= y < self.height:
                            # 80% chance of permanent fault in the hot zone
                            if random.random() < 0.8:
                                self.faults.add((x, y))
                                self.grid[y][x] = 1

    def trigger_thermal_event(self, qx, qy, intensity=10.0):
        """Simulates a sudden heat spike in a specific quadrant."""
        self.thermal_zones[qy][qx] = intensity
        
    def apply_cooling(self, qx, qy):
        """Physical hardware cools the quadrant back down to baseline."""
        self.thermal_zones[qy][qx] = 1.0

    def tick(self):
        """Advances simulation by one time step."""
        new_grid = copy.deepcopy(self.grid)
        
        for y in range(self.height):
            for x in range(self.width):
                # Skip sleeping zones entirely
                if (x, y) in self.sleep_zones:
                    if new_grid[y][x] != -2:
                        new_grid[y][x] = 0
                    continue
                    
                # Skip Physical Voids (-2) and Quarantined nodes (-1)
                if self.grid[y][x] == -1:
                    new_grid[y][x] = -1
                    continue
                elif self.grid[y][x] == -2:
                    new_grid[y][x] = -2
                    continue
                    
                # 1. Spontaneous Noise
                if self.grid[y][x] == 0:
                    # Calculate local thermal multiplier based on quadrant
                    qx = 0 if x < self.width // 2 else 1
                    qy = 0 if y < self.height // 2 else 1
                    local_multiplier = self.thermal_zones[qy][qx]
                    local_noise_rate = self.noise_rate * local_multiplier
                    
                    if random.random() < local_noise_rate or (x, y) in self.faults:
                        new_grid[y][x] = 1
                else:
                    # 2. Age existing errors
                    new_grid[y][x] += 1
                    
                    # 3. Cascade Logic (Infect neighbors if error is too old)
                    if new_grid[y][x] >= self.cascade_threshold:
                        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < self.width and 0 <= ny < self.height:
                                # Neighbor becomes infected (age 1) if it was healthy (0)
                                if self.grid[ny][nx] == 0:
                                    new_grid[ny][nx] = 1

        self.grid = new_grid

    def apply_correction(self, x, y):
        """External control mechanism to quench an error."""
        if 0 <= x < self.width and 0 <= y < self.height:
            if self.grid[y][x] != -1: # Don't quench isolated nodes
                self.grid[y][x] = 0
                
    def isolate_node(self, x, y):
        """Structurally isolate a degraded node so it cannot cascade."""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.grid[y][x] = -1

    def get_syndrome_snapshot(self):
        """Returns a boolean mask of errors for global decoders."""
        return [[1 if cell > 0 else 0 for cell in row] for row in self.grid]
        
    def get_error_count(self):
        count = 0
        for row in self.grid:
            for cell in row:
                if cell > 0: count += 1
        return count
