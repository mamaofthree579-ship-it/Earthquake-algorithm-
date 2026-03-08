import uuid
from datetime import datetime


class ScientificMemoryGraph:

    def __init__(self):

        self.nodes = {}
        self.edges = []

    # -------------------------------------------------
    # Add Experiment Node
    # -------------------------------------------------

    def add_experiment(self, parameters, result, governance_score):

        node_id = str(uuid.uuid4())

        node = {
            "id": node_id,
            "timestamp": datetime.utcnow().isoformat(),
            "parameters": parameters,
            "result": result,
            "governance_score": governance_score
        }

        self.nodes[node_id] = node

        return node_id

    # -------------------------------------------------
    # Connect Experiments
    # -------------------------------------------------

    def connect(self, node_a, node_b, relation="similar"):

        edge = {
            "from": node_a,
            "to": node_b,
            "relation": relation
        }

        self.edges.append(edge)

    # -------------------------------------------------
    # Get Best Experiments
    # -------------------------------------------------

    def best_experiments(self, top_k=5):

        ranked = sorted(
            self.nodes.values(),
            key=lambda x: x["governance_score"],
            reverse=True
        )

        return ranked[:top_k]

    # -------------------------------------------------
    # Graph Summary
    # -------------------------------------------------

    def summary(self):

        return {
            "total_experiments": len(self.nodes),
            "connections": len(self.edges)
        }
