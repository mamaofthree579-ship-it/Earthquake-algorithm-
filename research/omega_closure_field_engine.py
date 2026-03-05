import numpy as np


class OmegaClosureFieldEngine:

    def __init__(self):

        self.entropy_weight = 0.4
        self.novelty_weight = 0.3
        self.redundancy_weight = 0.2
        self.divergence_weight = 0.1

        self.history = []

    # -------------------------------------------------
    # Field Metrics
    # -------------------------------------------------

    def entropy_field(self, state):

        state = np.array(state) + 1e-12

        hist, _ = np.histogram(state, bins=50, density=True)

        hist = hist + 1e-12

        return float(-np.sum(hist * np.log(hist)))

    def novelty_field(self, state):
        return float(np.var(state))

    def redundancy_field(self, state):

        unique_ratio = len(set(np.round(state, 6))) / len(state)

        return float(1 - unique_ratio)

    def divergence_field(self, state):

        return float(np.mean(np.abs(np.gradient(state))))

    # -------------------------------------------------
    # Closure Stability Functional
    # -------------------------------------------------

    def evaluate(self, state_vector):

        entropy = self.entropy_field(state_vector)
        novelty = self.novelty_field(state_vector)
        redundancy = self.redundancy_field(state_vector)
        divergence = self.divergence_field(state_vector)

        closure_score = (
            self.entropy_weight * entropy +
            self.novelty_weight * novelty -
            self.redundancy_weight * redundancy -
            self.divergence_weight * divergence
        )

        self.history.append(closure_score)

        return {
            "omega_closure_stability": float(closure_score),
            "field_metrics": {
                "entropy": entropy,
                "novelty": novelty,
                "redundancy": redundancy,
                "divergence": divergence
            }
        }
