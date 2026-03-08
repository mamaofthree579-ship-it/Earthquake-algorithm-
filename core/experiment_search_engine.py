class AutomatedExperimentSearchEngine:

    def __init__(self, civilization_kernel, adaptive_ai=None):

        self.kernel = civilization_kernel
        self.adaptive_ai = adaptive_ai
        self.search_history = []

    def generate_parameters(self):

        if self.adaptive_ai:
            return self.adaptive_ai.generate_parameters()

        return {"t": np.random.randint(0, 365)}

    def run_experiment(self, engine, df):

        params = self.generate_parameters()

        cycle = self.kernel.run_cycle(engine, df)

        self.search_history.append(cycle)

        return cycle

    def run_batch(self, engine, df, n=5):

        results = []

        for _ in range(n):

            result = self.run_experiment(engine, df)

            results.append(result)

        return results

    def best_experiments(self, top_k=5):

        ranked = sorted(
            self.search_history,
            key=lambda x: x["governance_index"],
            reverse=True
        )

        return ranked[:top_k]
