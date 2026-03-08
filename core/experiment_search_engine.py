import numpy as np


class AutomatedExperimentSearchEngine:

    def __init__(self, civilization_kernel):

        self.kernel = civilization_kernel
        self.search_history = []

    # -------------------------------------------------
    # Random Parameter Generator
    # -------------------------------------------------

    def generate_parameters(self):

        params = {
            "t": int(np.random.randint(0, 365))
        }

        return params

    # -------------------------------------------------
    # Run Single Experiment
    # -------------------------------------------------

    def run_experiment(self, engine, df):

        cycle = self.kernel.run_cycle(engine, df)

        self.search_history.append(cycle)

        return cycle

    # -------------------------------------------------
    # Run Multiple Experiments
    # -------------------------------------------------

    def run_batch(self, engine, df, n=5):

        results = []

        for _ in range(n):

            result = self.run_experiment(engine, df)

            results.append(result)

        return results

    # -------------------------------------------------
    # Best Experiments
    # -------------------------------------------------

    def best_experiments(self, top_k=5):

        ranked = sorted(
            self.search_history,
            key=lambda x: x["governance_index"],
            reverse=True
        )

        return ranked[:top_k]
