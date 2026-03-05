import numpy as np


class UniversalKnowledgeMeshCore:

    def __init__(self):

        self.discovery_weight = 0.4
        self.communication_weight = 0.3
        self.stability_weight = 0.2
        self.entropy_weight = 0.1

        self.mesh_history = []

    # ----------------------------------------
    # Discovery Emergence Operator
    # ----------------------------------------

    def discovery_operator(self, field):

        grad = np.gradient(field)

        return np.mean(np.abs(grad))

    # ----------------------------------------
    # Communication Diffusion Operator
    # ----------------------------------------

    def communication_operator(self, field):

        return np.std(field)

    # ----------------------------------------
    # Stability Preservation Operator
    # ----------------------------------------

    def stability_operator(self, field):

        return np.mean(field)

    # ----------------------------------------
    # Entropy Diversity Operator
    # ----------------------------------------

    def entropy_operator(self, field):

        field = np.array(field) + 1e-12

        hist, _ = np.histogram(field, bins=50, density=True)

        hist = hist + 1e-12

        return float(-np.sum(hist * np.log(hist)))

    # ----------------------------------------
    # Mesh State Evaluation
    # ----------------------------------------

    def evaluate_mesh(self, field_state):

        discovery = self.discovery_operator(field_state)
        communication = self.communication_operator(field_state)
        stability = self.stability_operator(field_state)
        entropy = self.entropy_operator(field_state)

        mesh_score = (
            self.discovery_weight * discovery +
            self.communication_weight * communication +
            self.stability_weight * stability +
            self.entropy_weight * entropy
        )

        self.mesh_history.append(mesh_score)

        return {
            "universal_mesh_coherence_score": float(mesh_score),
            "mesh_metrics": {
                "discovery_field": discovery,
                "communication_field": communication,
                "stability_field": stability,
                "entropy_field": entropy
            }
        }
