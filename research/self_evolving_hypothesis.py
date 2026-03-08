import numpy as np

class SelfEvolvingHypothesisEngine:

    def __init__(self, memory_graph, meta_kernel, adaptive_ai):
        self.memory_graph = memory_graph
        self.meta_kernel = meta_kernel
        self.adaptive_ai = adaptive_ai

    # -------------------------------
    # Generate candidate hypotheses
    # -------------------------------
    def generate_candidates(self, n=5):
        candidates = []
        for i in range(n):
            params = self.adaptive_ai.generate_parameters()
            # Randomly combine with Meta-OS discovery outputs
            meta_vector = np.random.randn(10)
            hypothesis_vector = np.concatenate([np.array(list(params.values())), meta_vector[:len(params)]])
            candidates.append({
                "id": f"hypo_{i}_{np.random.randint(1000,9999)}",
                "parameters": params,
                "vector": hypothesis_vector
            })
        return candidates

    # -------------------------------
    # Evaluate internal consistency
    # -------------------------------
    def evaluate_consistency(self, candidate):
        vec = candidate["vector"]
        score = 1 / (1 + np.exp(-np.mean(vec)))
        return float(score)

    # -------------------------------
    # Rank and select hypotheses
    # -------------------------------
    def rank_candidates(self, candidates):
        ranked = []
        for c in candidates:
            c["consistency_score"] = self.evaluate_consistency(c)
            ranked.append(c)
        # Sort descending
        ranked.sort(key=lambda x: x["consistency_score"], reverse=True)
        return ranked

    # -------------------------------
    # Full autonomous discovery cycle
    # -------------------------------
    def discovery_cycle(self, n_candidates=5):
        candidates = self.generate_candidates(n_candidates)
        ranked = self.rank_candidates(candidates)
        # Store top candidate in memory graph
        if ranked:
            self.memory_graph.add_experiment(
                parameters=ranked[0]["parameters"],
                result={"consistency_score": ranked[0]["consistency_score"]},
                governance_index=None
            )
        return ranked
