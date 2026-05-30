import heapq
import math

class Hippocampus:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        
        # 0.0 = safe, 1.0 = known permanent fault
        # We use a float to allow "danger gradients" around faults
        self.fault_map = [[0.0 for _ in range(width)] for _ in range(height)]
        
    def register_fault(self, x, y):
        """Called by Sentinel Agents when a node is plastically down-regulated."""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.fault_map[y][x] = 1.0
            
            # Radiate danger to immediate neighbors to create a buffer zone
            # This teaches the router to stay away from the edge of hot zones
            for dy in [-1, 0, 1]:
                for dx in [-1, 0, 1]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.width and 0 <= ny < self.height:
                        if self.fault_map[ny][nx] < 1.0:
                            self.fault_map[ny][nx] = max(self.fault_map[ny][nx], 0.5)

    def route_path(self, start, end):
        """
        Uses A* to find the safest path across the quantum fabric.
        Avoids nodes with high fault probabilities.
        """
        sx, sy = start
        ex, ey = end
        
        # If start or end is actually a fault, routing fails immediately
        if self.fault_map[sy][sx] == 1.0 or self.fault_map[ey][ex] == 1.0:
            return None

        # Priority queue for A*
        queue = []
        heapq.heappush(queue, (0, start))
        
        came_from = {}
        cost_so_far = {}
        
        came_from[start] = None
        cost_so_far[start] = 0
        
        while queue:
            current_priority, current_node = heapq.heappop(queue)
            cx, cy = current_node
            
            if current_node == end:
                break
                
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
                nx, ny = cx + dx, cy + dy
                
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    next_node = (nx, ny)
                    fault_risk = self.fault_map[ny][nx]
                    
                    if fault_risk == 1.0:
                        continue # Physically impossible to route through a dead node
                        
                    # Base cost is distance (sqrt(2) for diagonals, 1 for straight)
                    base_cost = math.sqrt(dx*dx + dy*dy)
                    
                    # Danger penalty makes the router curve away from hot zones
                    danger_penalty = fault_risk * 10.0
                    
                    new_cost = cost_so_far[current_node] + base_cost + danger_penalty
                    
                    if next_node not in cost_so_far or new_cost < cost_so_far[next_node]:
                        cost_so_far[next_node] = new_cost
                        
                        # Heuristic is euclidean distance to end
                        heuristic = math.sqrt((ex - nx)**2 + (ey - ny)**2)
                        priority = new_cost + heuristic
                        
                        heapq.heappush(queue, (priority, next_node))
                        came_from[next_node] = current_node

        # Reconstruct path
        if end not in came_from:
            return None # No valid path found
            
        path = []
        current = end
        while current != start:
            path.append(current)
            current = came_from[current]
        path.append(start)
        path.reverse()
        
        return path
