class QuarantineManager:
    def __init__(self, logger):
        self.logger = logger

    def execute_quarantines(self, decisions, topology_map):
        isolated = []
        for node, decision in decisions.items():
            if decision == "QUARANTINE_REQUIRED":
                topology_map["nodes"][node]["status"] = "QUARANTINED"
                isolated.append(node)
                self.logger.log("QUARANTINE_MANAGER", "NODE_ISOLATED", {"node": node})
        return topology_map, isolated
