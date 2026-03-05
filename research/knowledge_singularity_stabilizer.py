import numpy as np


class KnowledgeCoherenceSingularityStabilizer:

    def __init__(self):

        # Stability tuning coefficients
        self.alpha_entropy = 0.4
        self.beta_novelty = 0.3
        self.gamma_redundancy = 0.2
        self.delta_coherence = 0.1

        self.history = []

    # -----------------------------
    # Entropy Proxy Metric
    # -----------------------------

    def entropy_metric(self, signal):

        signal = np.array(signal) + 1e-12

        hist, _ = np.histogram(signal, bins=50, density=True)

        hist = hist + 1e-12

        return float(-np.sum(hist * np.log(hist)))

    # -----------------------------
    # Novelty Field Metric
    # -----------------------------

    def novelty_metric(self, signal):

        return float(np.var(signal))

    # -----------------------------
    # Redundancy Metric
    # -----------------------------

    def redundancy_metric(self, signal):

        unique_ratio = len(set(np.round(signal, 5))) / len(signal)

        return float(1 - unique_ratio)

    # -----------------------------
    # Coherence Metric
    # -----------------------------

    def coherence_metric(self, signal):

        return float(np.mean(signal))

    # -----------------------------
    # Singularity Stability Score
    # -----------------------------

    def stabilize(self, signal):

        signal = list(signal)

        entropy = self.entropy_metric(signal)
        novelty = self.novelty_metric(signal)
        redundancy = self.redundancy_metric(signal)
        coherence = self.coherence_metric(signal)

        stability_score = (
            self.alpha_entropy * entropy +
            self.beta_novelty * novelty -
            self.gamma_redundancy * redundancy +
            self.delta_coherence * coherence
        )

        self.history.append(stability_score)

        return {
            "stability_score": float(stability_score),
            "metrics": {
                "entropy": entropy,
                "novelty": novelty,
                "redundancy": redundancy,
                "coherence": coherence
            }
        }
