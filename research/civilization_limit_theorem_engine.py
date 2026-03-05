import numpy as np


class CivilizationLimitTheoremEngine:

    def __init__(self):

        self.entropy_weight = 0.4
        self.novelty_weight = 0.3
        self.redundancy_weight = 0.2
        self.coherence_weight = 0.1

        self.history = []

    # -----------------------------
    # Entropy Diversity Field
    # -----------------------------

    def entropy_field(self, state):

        state = np.array(state) + 1e-12

        hist, _ = np.histogram(state, bins=50, density=True)

        hist = hist + 1e-12

        return float(-np.sum(hist * np.log(hist)))

    # -----------------------------
    # Novelty Emergence Field
    # -----------------------------

    def novelty_field(self, state):

        return float(np.var(state))

    # -----------------------------
    # Redundancy Collapse Risk
    # -----------------------------

    def redundancy_field(self, state):

        unique_ratio = len(set(np.round(state, 6))) / len(state)

        return float(1 - unique_ratio)

    # -----------------------------
    # Structural Coherence Field
    # -----------------------------

    def coherence_field(self, state):

        return float(np.mean(state))

    # -----------------------------
    # Civilization Stability Functional
    # -----------------------------

    def evaluate(self, state_vector):

        entropy = self.entropy_field(state_vector)
        novelty = self.novelty_field(state_vector)
        redundancy = self.redundancy_field(state_vector)
        coherence = self.coherence_field(state_vector)

        limit_score = (
            self.entropy_weight * entropy +
            self.novelty_weight * novelty -
            self.redundancy_weight * redundancy +
            self.coherence_weight * coherence
        )

        self.history.append(limit_score)

        return {
            "civilization_limit_score": float(limit_score),
            "metrics": {
                "entropy": entropy,
                "novelty": novelty,
                "redundancy": redundancy,
                "coherence": coherence
            }
        }
