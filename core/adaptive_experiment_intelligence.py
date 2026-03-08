import numpy as np


class AdaptiveExperimentIntelligence:

    def __init__(self, memory_graph):

        self.memory_graph = memory_graph

    # -------------------------------------------------
    # Estimate Best Parameter Region
    # -------------------------------------------------

    def estimate_best_parameter(self):

        experiments = list(self.memory_graph.nodes.values())

        if len(experiments) == 0:
            return {"t": np.random.randint(0, 365)}

        top = sorted(
            experiments,
            key=lambda x: x["governance_score"],
            reverse=True
        )[:5]

        avg_t = int(
            np.mean([exp["parameters"]["t"] for exp in top])
        )

        return {"t": avg_t}

    # -------------------------------------------------
    # Generate Adaptive Parameter
    # -------------------------------------------------

    def generate_parameters(self):

        best_region = self.estimate_best_parameter()

        t = best_region["t"]

        variation = np.random.randint(-20, 20)

        candidate = max(0, min(365, t + variation))

        return {"t": candidate}
