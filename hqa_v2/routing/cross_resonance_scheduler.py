from hippocampus_router import HippocampusRouter

class CrossResonanceScheduler:
    """
    Sits above the single-path Hippocampus Router.
    Scans the physical topology for the most pristine physical edge (pair of nodes),
    and commands the Hippocampus to simultaneously route two logical quantum states
    to that edge for a two-qubit entangling gate.
    """
    def __init__(self, logger, topology_map):
        self.logger = logger
        self.nodes = topology_map["nodes"]
        self.edges = topology_map["edges"]
        self.topology_map = topology_map
        self.router = HippocampusRouter(topology_map)

    def _find_best_physical_pair(self):
        """Scans the lattice for a connected pair with max coherence and min risk."""
        best_pair = None
        highest_score = -1.0
        
        for node_a, neighbors in self.edges.items():
            for node_b in neighbors:
                if self.nodes[node_a]["status"] == "STABLE" and self.nodes[node_b]["status"] == "STABLE":
                    # Simple heuristic: combined coherence minus proximity risk
                    score = self.nodes[node_a]["coherence"] + self.nodes[node_b]["coherence"]
                    # Penalize if they are near a quarantined node
                    risk_a = self.router._calculate_risk_cost(node_a)
                    risk_b = self.router._calculate_risk_cost(node_b)
                    
                    if risk_a != float('inf') and risk_b != float('inf'):
                        score -= (risk_a + risk_b) * 0.1
                        
                        if score > highest_score:
                            highest_score = score
                            best_pair = (node_a, node_b)
                            
        return best_pair

    def schedule_two_qubit_gate(self, logical_a_current, logical_b_current):
        """Routes two logical states to a shared physical edge for a CR pulse."""
        self.logger.log("CR_SCHEDULER", "ENTANGLING_GATE_REQUESTED", {"logical_a": logical_a_current, "logical_b": logical_b_current})
        
        target_pair = self._find_best_physical_pair()
        if not target_pair:
            self.logger.log("CR_SCHEDULER", "SCHEDULING_FAILED", {"reason": "no_pristine_edges_available"})
            return None, None
            
        target_a, target_b = target_pair
        self.logger.log("CR_SCHEDULER", "TARGET_EDGE_SELECTED", {"target_edge": [target_a, target_b]})
        
        # Command Hippocampus to route A
        path_a = self.router.find_safest_path(logical_a_current, target_a)
        
        # Command Hippocampus to route B (Ensure it doesn't cross A's target)
        # For simplicity in this demo, we assume parallel non-intersecting capability,
        # but a true scheduler would lock A's path and run B over the residual graph.
        path_b = self.router.find_safest_path(logical_b_current, target_b)
        
        if path_a and path_b:
            self.logger.log("CR_SCHEDULER", "MULTI_ROUTE_SUCCESS", {"path_a": path_a, "path_b": path_b})
            return path_a, path_b
            
        self.logger.log("CR_SCHEDULER", "MULTI_ROUTE_FAILED", {"reason": "pathing_conflict"})
        return None, None
