from hippocampus_router import HippocampusRouter

class TopologyRouter:
    def __init__(self, logger):
        self.logger = logger

    def reroute_circuit(self, topology_map, start_node, end_node):
        self.logger.log("HIPPOCAMPUS", "ROUTING_REQUESTED", {"start": start_node, "end": end_node})
        
        router = HippocampusRouter(topology_map)
        path = router.find_safest_path(start_node, end_node)
        
        if not path:
            self.logger.log("HIPPOCAMPUS", "SYSTEMIC_QUENCH", {"reason": "no_safe_path_found"})
            return None
            
        self.logger.log("HIPPOCAMPUS", "REROUTE_SUCCESS", {"new_path": path})
        return path
