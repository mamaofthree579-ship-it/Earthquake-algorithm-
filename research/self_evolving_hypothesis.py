import numpy as np

class SelfEvolvingHypothesisEngine:
    def __init__(self, memory_graph, meta_kernel, adaptive_ai):
        self.memory_graph = memory_graph
        self.meta_kernel = meta_kernel
        self.adaptive_ai = adaptive_ai

    def generate_candidates(self, n=5):
        candidates = []
        for i in range(n):
            params = self.adaptive_ai.generate_parameters()
            meta_vector = np.random.randn(10)
            hypothesis_vector = np.concatenate([np.array(list(params.values())), meta_vector[:len(params)]])
            candidates.append({
                "id": f"hypo_{i}_{np.random.randint(1000,9999)}",
                "parameters": params,
                "vector": hypothesis_vector
            })
        return candidates

    def evaluate_consistency(self, candidate):
        vec = candidate["vector"]
        return float(1 / (1 + np.exp(-np.mean(vec))))

    def rank_candidates(self, candidates):
        ranked = []
        for c in candidates:
            c["consistency_score"] = self.evaluate_consistency(c)
            ranked.append(c)
        ranked.sort(key=lambda x: x["consistency_score"], reverse=True)
        return ranked

    def discovery_cycle(self, n_candidates=5):
        candidates = self.generate_candidates(n_candidates)
        ranked = self.rank_candidates(candidates)
        if not ranked:
            return []
        top_candidate = ranked[0]
        try:
            self.memory_graph.add_experiment(
                parameters=top_candidate["parameters"],
                result={"consistency_score": top_candidate["consistency_score"]},
                governance_index=float(top_candidate["consistency_score"]) if top_candidate["consistency_score"] is not None else 0.0
            )
        except Exception:
            pass
        return ranked
