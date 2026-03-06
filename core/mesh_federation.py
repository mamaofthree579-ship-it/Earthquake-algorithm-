import requests
import uuid


class MeshFederation:

    def __init__(self):

        self.nodes = {}
        self.experiments = {}

    # -----------------------------------------
    # Node Registration
    # -----------------------------------------

    def register_node(self, name, endpoint):

        node_id = str(uuid.uuid4())

        self.nodes[node_id] = {
            "name": name,
            "endpoint": endpoint
        }

        return node_id

    # -----------------------------------------
    # List Nodes
    # -----------------------------------------

    def list_nodes(self):

        return self.nodes

    # -----------------------------------------
    # Dispatch Job to Node
    # -----------------------------------------

    def dispatch_job(self, node_id, payload):

        if node_id not in self.nodes:
            return {"error": "node not found"}

        node = self.nodes[node_id]

        try:

            r = requests.post(
                f"{node['endpoint']}/submit_job",
                json=payload,
                timeout=10
            )

            return r.json()

        except Exception as e:

            return {"error": str(e)}

    # -----------------------------------------
    # Register Experiment Globally
    # -----------------------------------------

    def register_experiment(self, name, metadata):

        exp_id = str(uuid.uuid4())

        self.experiments[exp_id] = {
            "name": name,
            "metadata": metadata
        }

        return exp_id

    # -----------------------------------------
    # List Experiments
    # -----------------------------------------

    def list_experiments(self):

        return self.experiments
