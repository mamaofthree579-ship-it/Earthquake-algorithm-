import numpy as np


class SelfReferentialDiscoveryLoop:

    def __init__(self):

        self.novelty_weight = 0.4
        self.entropy_weight = 0.3
        self.redundancy_weight = 0.2
        self.coherence_weight = 0.1

        self.history = []

    # ----------------------------------------
    # Discovery Evaluation Metrics
    # ----------------------------------------

    def novelty_metric(self, results):

        if len(results) < 2:
            return 0.0

        return float(np.var(results))

    def entropy_metric(self, results):

        hist, _ = np.histogram(results, bins=30, density=True)

        hist = hist + 1e-12

        return float(-np.sum(hist * np.log(hist)))

    def redundancy_metric(self, results):

        unique_ratio = len(set(np.round(results, 4))) / len(results)

        return float(1 - unique_ratio)

    def coherence_metric(self, results):

        return float(np.mean(results))

    # ----------------------------------------
    # Adaptive Learning Cycle
    # ----------------------------------------

    def learning_cycle(self, discovery_output):

        results = discovery_output["results"]

        novelty = self.novelty_metric(results)
        entropy = self.entropy_metric(results)
        redundancy = self.redundancy_metric(results)
        coherence = self.coherence_metric(results)

        score = (
            self.novelty_weight * novelty +
            self.entropy_weight * entropy -
            self.redundancy_weight * redundancy +
            self.coherence_weight * coherence
        )

        self.history.append(score)

        return {
            "self_learning_score": float(score),
            "metrics": {
                "novelty": novelty,
                "entropy": entropy,
                "redundancy": redundancy,
                "coherence": coherence
            }
        }
