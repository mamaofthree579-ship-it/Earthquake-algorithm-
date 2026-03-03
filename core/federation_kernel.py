import numpy as np

class FederationKernel:

    def __init__(self):
        self.node_registry = {}

    def register_node(self, node_id, health_score):

        self.node_registry[node_id] = health_score

    def select_compute_node(self):

        if not self.node_registry:
            return None

        return max(
            self.node_registry.items(),
            key=lambda x: x[1]
        )[0]
