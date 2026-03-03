import numpy as np

class DiscoveryFabric:

    def __init__(self):
        self.workflow_registry = []

    def register_workflow(self, workflow_name):

        self.workflow_registry.append(workflow_name)

    def suggest_workflow(self):

        if not self.workflow_registry:
            return "No workflows registered"

        return np.random.choice(self.workflow_registry)
