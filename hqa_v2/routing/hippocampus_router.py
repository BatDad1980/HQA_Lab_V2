import heapq
import math

class HippocampusRouter:
    """
    A* routing algorithm with advanced risk-scoring.
    Finds the optimal path across the physical topology while avoiding quarantined
    nodes and penalizing routes that pass near degraded areas.
    """
    def __init__(self, topology_map):
        self.nodes = topology_map["nodes"]
        self.edges = topology_map["edges"]

    def _heuristic(self, a_id, b_id):
        ax, ay = self.nodes[a_id]["x"], self.nodes[a_id]["y"]
        bx, by = self.nodes[b_id]["x"], self.nodes[b_id]["y"]
        return math.hypot(ax - bx, ay - by)

    def _calculate_risk_cost(self, node_id):
        """Calculates risk proximity. Penalizes nodes near degraded/quarantined areas."""
        base_cost = 1.0
        status = self.nodes[node_id]["status"]
        error_type = self.nodes[node_id].get("error_type", "GENERIC")
        
        if status == "QUARANTINED" or status == "UNSTABLE":
            return float('inf') # Impassable
            
        if status == "DEGRADED":
            base_cost += 5.0 # High penalty for using a degraded node
            
        # Check neighbors for risk proximity
        for neighbor in self.edges[node_id]:
            n_status = self.nodes[neighbor]["status"]
            n_error_type = self.nodes[neighbor].get("error_type", "GENERIC")
            
            if n_status == "QUARANTINED":
                # For cat qubits, phase flips are the only vector, so we highly penalize routing near a Z-error source
                if n_error_type == "PHASE_FLIP":
                    base_cost += 8.0 # Extreme proximity penalty for phase flips
                else:
                    base_cost += 3.0 # Standard proximity penalty
            elif n_status == "DEGRADED":
                base_cost += 1.0 # Mild proximity penalty
                
        return base_cost

    def find_safest_path(self, start_id, end_id):
        # Standard A* algorithm
        frontier = []
        heapq.heappush(frontier, (0, start_id))
        came_from = {start_id: None}
        cost_so_far = {start_id: 0}

        while frontier:
            _, current = heapq.heappop(frontier)

            if current == end_id:
                break

            for next_node in self.edges[current]:
                risk_cost = self._calculate_risk_cost(next_node)
                if risk_cost == float('inf'):
                    continue # Cannot pass

                new_cost = cost_so_far[current] + risk_cost
                if next_node not in cost_so_far or new_cost < cost_so_far[next_node]:
                    cost_so_far[next_node] = new_cost
                    priority = new_cost + self._heuristic(next_node, end_id)
                    heapq.heappush(frontier, (priority, next_node))
                    came_from[next_node] = current

        if end_id not in came_from:
            return None # No path found

        # Reconstruct path
        path = []
        current = end_id
        while current is not None:
            path.append(current)
            current = came_from[current]
        path.reverse()
        
        return path
