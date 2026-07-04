import copy

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
        
        # Command Hippocampus to route A.
        path_a = self.router.find_safest_path(logical_a_current, target_a)
        if not path_a:
            self.logger.log("CR_SCHEDULER", "MULTI_ROUTE_FAILED", {"reason": "no_path_for_a"})
            return None, None

        # Route B over the residual graph: reserve every node on A's path so the two
        # entangling routes cannot claim the same physical qubit. B's own endpoints
        # stay routable so it can still leave its start and reach its target.
        #
        # This is a greedy spatial reservation (A is routed first). It removes mid-path
        # contention but does not resolve endpoint contention (when the chosen pair
        # forces one route through the other's target) and does not guarantee an
        # optimal joint schedule. A full spatiotemporal scheduler remains future work.
        residual = copy.deepcopy(self.topology_map)
        for node_id in path_a:
            if node_id not in (logical_b_current, target_b):
                residual["nodes"][node_id]["status"] = "QUARANTINED"
        path_b = HippocampusRouter(residual).find_safest_path(logical_b_current, target_b)

        if path_a and path_b:
            self.logger.log("CR_SCHEDULER", "MULTI_ROUTE_SUCCESS", {"path_a": path_a, "path_b": path_b})
            return path_a, path_b
            
        self.logger.log("CR_SCHEDULER", "MULTI_ROUTE_FAILED", {"reason": "pathing_conflict"})
        return None, None
