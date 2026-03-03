import numpy as np

class FederationKernel:

    def __init__(self):
        self.nodes = {}

    def register_node(self, node_id, health):
        self.nodes[node_id] = health

    def select_node(self):

        if not self.nodes:
            return None

        return max(
            self.nodes.items(),
            key=lambda x:x[1]
        )[0]
