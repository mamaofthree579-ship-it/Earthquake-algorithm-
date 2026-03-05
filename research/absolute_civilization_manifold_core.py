import numpy as np


class AbsoluteCivilizationKnowledgeManifoldCore:

    def __init__(self):

        self.entropy_weight = 0.35
        self.novelty_weight = 0.25
        self.redundancy_weight = 0.2
        self.coherence_weight = 0.2

        self.manifold_history = []

    # --------------------------------------------------
    # Field Operators
    # --------------------------------------------------

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

    def coherence_field(self, state):
        return float(np.mean(state))

    def divergence_field(self, state):
        return float(np.mean(np.abs(np.gradient(state))))

    # --------------------------------------------------
    # Manifold Closure Functional
    # --------------------------------------------------

    def evaluate_manifold(self, state_vector):

        entropy = self.entropy_field(state_vector)
        novelty = self.novelty_field(state_vector)
        redundancy = self.redundancy_field(state_vector)
        coherence = self.coherence_field(state_vector)
        divergence = self.divergence_field(state_vector)

        manifold_score = (
            self.entropy_weight * entropy +
            self.novelty_weight * novelty -
            self.redundancy_weight * redundancy +
            self.coherence_weight * coherence -
            0.1 * divergence
        )

        self.manifold_history.append(manifold_score)

        return {
            "absolute_manifold_stability": float(manifold_score),
            "manifold_metrics": {
                "entropy_field": entropy,
                "novelty_field": novelty,
                "redundancy_field": redundancy,
                "coherence_field": coherence,
                "divergence_field": divergence
            }
        }
