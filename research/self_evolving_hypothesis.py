def discovery_cycle(self, n_candidates=5):

    candidates = self.generate_candidates(n_candidates)
    ranked = self.rank_candidates(candidates)

    # Nothing generated safely
    if not ranked:
        return []

    # Safely store top hypothesis
    top_candidate = ranked[0]

    try:
        self.memory_graph.add_experiment(
            parameters=top_candidate["parameters"],
            result={
                "consistency_score": top_candidate["consistency_score"]
            },
            governance_index=float(top_candidate["consistency_score"])
            if top_candidate["consistency_score"] is not None
            else 0.0
        )
    except Exception:
        # Fail-safe storage attempt
        pass

    return ranked
