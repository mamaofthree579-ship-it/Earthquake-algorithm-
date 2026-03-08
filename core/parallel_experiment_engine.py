import multiprocessing as mp


class ParallelExperimentEngine:

    def __init__(self, experiment_search, memory_graph):

        self.search_engine = experiment_search
        self.memory_graph = memory_graph

    # -------------------------------------------------
    # Worker
    # -------------------------------------------------

    def worker(self, args):

        engine, df = args

        result = self.search_engine.run_experiment(engine, df)

        return result

    # -------------------------------------------------
    # Run Parallel Batch
    # -------------------------------------------------

    def run_parallel_batch(self, engine, df, n=10):

        pool = mp.Pool(mp.cpu_count())

        tasks = [(engine, df) for _ in range(n)]

        results = pool.map(self.worker, tasks)

        pool.close()
        pool.join()

        for r in results:

            try:
                self.memory_graph.add_experiment(
                    r["parameters"],
                    r["result"],
                    r["governance_index"]
                )
            except Exception:
                pass

        return results
