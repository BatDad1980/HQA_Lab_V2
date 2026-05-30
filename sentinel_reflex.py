class SentinelAgent:
    def __init__(self, fabric, x_start, y_start, width, height, plasticity_threshold=5, hippocampus=None):
        self.fabric = fabric
        self.x_start = x_start
        self.y_start = y_start
        self.width = width
        self.height = height
        self.hippocampus = hippocampus
        
        self.plasticity_threshold = plasticity_threshold
        self.fault_counters = {} # Tracks how many times a node flipped
        self.down_regulated_nodes = set() # Nodes ignored via plastic remapping
        
        self.local_corrections = 0
        self.last_tick_corrections = 0
        
        # Pillar 3: Sleep Cycles & Synaptic Pruning
        self.sleep_threshold = 30 # Total accumulated noise before forcing a sleep
        self.sleep_timer = 0
        self.sleep_duration = 3
        
    def get_memory_footprint(self):
        # A sentinel only loads its local patch into memory
        return self.width * self.height

    def initiate_sleep(self):
        """Puts this entire patch to sleep to clear metabolic waste (noise)."""
        print(f"[SENTINEL] Patch at ({self.x_start}, {self.y_start}) entering micro-sleep to prune noise.")
        self.sleep_timer = self.sleep_duration
        self.fault_counters.clear() # Synaptic pruning
        for dy in range(self.height):
            for dx in range(self.width):
                self.fabric.enter_sleep(self.x_start + dx, self.y_start + dy)
                
    def awaken(self):
        """Wakes the patch back up."""
        print(f"[SENTINEL] Patch at ({self.x_start}, {self.y_start}) waking up refreshed.")
        for dy in range(self.height):
            for dx in range(self.width):
                self.fabric.awaken(self.x_start + dx, self.y_start + dy)

    def step(self):
        """Zero-latency local processing tick."""
        if self.sleep_timer > 0:
            self.sleep_timer -= 1
            if self.sleep_timer == 0:
                self.awaken()
            return # Skip physics and correction while sleeping
            
        # Check if we need to sleep due to high accumulated noise (not permanent faults yet)
        total_noise_accumulated = sum(self.fault_counters.values())
        if total_noise_accumulated >= self.sleep_threshold:
            self.initiate_sleep()
            return
            
        for dy in range(self.height):
            for dx in range(self.width):
                gx = self.x_start + dx
                gy = self.y_start + dy
                
                # Boundary check
                if gx >= self.fabric.width or gy >= self.fabric.height:
                    continue
                    
                node_coord = (gx, gy)
                
                # Skip if down-regulated (Plastic Remapping)
                if node_coord in self.down_regulated_nodes:
                    continue
                    
                # Read local state
                if self.fabric.grid[gy][gx] > 0:
                    # Detect anomaly, track it
                    if node_coord not in self.fault_counters:
                        self.fault_counters[node_coord] = 0
                    self.fault_counters[node_coord] += 1
                    
                    # Plasticity check: is this a permanent hardware fault?
                    if self.fault_counters[node_coord] >= self.plasticity_threshold:
                        self.down_regulated_nodes.add(node_coord)
                        self.fabric.isolate_node(gx, gy)
                        # NEW IN V2: Report to Hippocampus
                        if self.hippocampus:
                            self.hippocampus.register_fault(gx, gy)
                    else:
                        # Instant localized quench
                        self.fabric.apply_correction(gx, gy)
                        self.local_corrections += 1

class HQANetwork:
    def __init__(self, fabric, patch_size=5, hippocampus=None):
        self.fabric = fabric
        self.hippocampus = hippocampus
        self.sentinels = []
        
        # Deploy sentinels across the fabric
        for y in range(0, fabric.height, patch_size):
            for x in range(0, fabric.width, patch_size):
                agent = SentinelAgent(fabric, x, y, patch_size, patch_size, hippocampus=self.hippocampus)
                self.sentinels.append(agent)
                
        self.total_corrections = 0
        self.peak_memory_footprint = 0
        self.down_regulated_count = 0
        
    def step(self):
        # In HQA, all sentinels process in parallel instantly at the edge
        # To calculate peak memory footprint, we only need the footprint of the largest parallel execution unit (1 patch).
        # We will sum them if we assume sequential simulation, but fundamentally the memory ceiling per core is just the patch size.
        # Let's track the maximum memory required per edge node.
        
        for sentinel in self.sentinels:
            sentinel.step()
            self.total_corrections += sentinel.local_corrections
            sentinel.last_tick_corrections = sentinel.local_corrections
            sentinel.local_corrections = 0
            
            mem = sentinel.get_memory_footprint()
            if mem > self.peak_memory_footprint:
                self.peak_memory_footprint = mem
                
        # Calculate plasticity savings
        self.down_regulated_count = sum(len(s.down_regulated_nodes) for s in self.sentinels)
