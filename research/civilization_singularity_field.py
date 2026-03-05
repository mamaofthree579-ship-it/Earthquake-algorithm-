import numpy as np


class CivilizationSingularityFieldCore:

    def __init__(self):

        self.alpha_entropy = 0.4
        self.beta_novelty = 0.3
        self.gamma_redundancy = 0.2
        self.delta_coherence = 0.1

        self.field_history = []

    # --------------------------------------
    # Entropy Field Operator
    # --------------------------------------

    def entropy_field(self, state):

        state = np.array(state) + 1e-12

        hist, _ = np.histogram(state, bins=50, density=True)

        hist = hist + 1e-12

        return float(-np.sum(hist * np.log(hist)))

    # --------------------------------------
    # Novelty Emergence Field
    # --------------------------------------

    def novelty_field(self, state):

        return float(np.var(state))

    # --------------------------------------
    # Redundancy Suppression Field
    # --------------------------------------

    def redundancy_field(self, state):

        unique_ratio = len(set(np.round(state, 6))) / len(state)

        return float(1 - unique_ratio)

    # --------------------------------------
    # Coherence Stabilization Field
    # --------------------------------------

    def coherence_field(self, state):

        return float(np.mean(state))

    # --------------------------------------
    # Singularity Stability Potential
    # --------------------------------------

    def evaluate_field(self, state_vector):

        entropy = self.entropy_field(state_vector)
        novelty = self.novelty_field(state_vector)
        redundancy = self.redundancy_field(state_vector)
        coherence = self.coherence_field(state_vector)

        potential = (
            self.alpha_entropy * entropy +
            self.beta_novelty * novelty -
            self.gamma_redundancy * redundancy +
            self.delta_coherence * coherence
        )

        self.field_history.append(potential)

        return {
            "civilization_singularity_potential": float(potential),
            "field_metrics": {
                "entropy": entropy,
                "novelty": novelty,
                "redundancy": redundancy,
                "coherence": coherence
            }
        }
