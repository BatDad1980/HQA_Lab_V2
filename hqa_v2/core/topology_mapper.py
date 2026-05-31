class TopologyMapper:
    """
    Defines a physical quantum topology (e.g., Heavy-Hex / Sparse Lattice).
    Provides explicit spatial coordinates and physical edges.
    """
    def __init__(self, width=5, height=5):
        self.width = width
        self.height = height
        self.nodes = {}
        self.edges = {}
        
        self._generate_sparse_lattice()

    def _generate_sparse_lattice(self):
        # Create a grid where only alternating nodes exist (sparse)
        for y in range(self.height):
            for x in range(self.width):
                if (x + y) % 2 == 0:  # Checkboard / sparse layout
                    node_id = f"Q_{x}_{y}"
                    self.nodes[node_id] = {"x": x, "y": y, "status": "STABLE", "coherence": 1.0}
                    self.edges[node_id] = []
                    
        # Create physical connections only to immediate available neighbors
        for node_id, data in self.nodes.items():
            x, y = data["x"], data["y"]
            potential_neighbors = [(x-1, y-1), (x+1, y-1), (x-1, y+1), (x+1, y+1)]
            for nx, ny in potential_neighbors:
                neighbor_id = f"Q_{nx}_{ny}"
                if neighbor_id in self.nodes:
                    self.edges[node_id].append(neighbor_id)

    def get_topology(self):
        return {"nodes": self.nodes, "edges": self.edges}
