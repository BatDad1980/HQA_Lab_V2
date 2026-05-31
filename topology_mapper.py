class TopologyMapper:
    @staticmethod
    def generate_heavy_hex_mask(width, height):
        """
        Generates a 2D boolean mask simulating a sparse, irregular Heavy-Hex lattice.
        True = Qubit exists (Silicon is present)
        False = Physical Void (Structural gap)
        """
        mask = [[True for _ in range(width)] for _ in range(height)]
        
        # Create an irregular honeycomb pattern by knocking out specific nodes
        for y in range(height):
            for x in range(width):
                # Simple heavy-hex approximation:
                # Every even row has gaps on odd columns
                # Every odd row has gaps on even columns, except every 3rd row which is a solid crossbar
                if y % 4 == 0:
                    if x % 2 != 0: mask[y][x] = False
                elif y % 4 == 1:
                    mask[y][x] = True # Crossbar
                elif y % 4 == 2:
                    if x % 2 == 0: mask[y][x] = False
                elif y % 4 == 3:
                    if x % 2 != 0: mask[y][x] = False # Another sparse row
                    
        return mask
        
    @staticmethod
    def generate_random_defects(width, height, defect_rate=0.1):
        """Generates a mostly square grid with random massive silicon voids."""
        import random
        mask = [[True for _ in range(width)] for _ in range(height)]
        for y in range(height):
            for x in range(width):
                if random.random() < defect_rate:
                    mask[y][x] = False
        return mask
