import random
from core.cluster_orchestrator import ClusterOrchestrator

class AutonomousDiscoveryEngine:

    def __init__(self):
        self.cluster = ClusterOrchestrator()

    def generate_hypothesis(self):
        """
        Generate experimental parameters automatically
        """
        params = {
            "x": random.uniform(-100, 100),
            "y": random.uniform(-100, 100),
            "noise": random.uniform(0, 1)
        }
        return params

    def experiment(self, params):
        """
        Example experiment function
        Replace with physics simulations later
        """
        x = params["x"]
        y = params["y"]
        noise = params["noise"]

        result = (x**2 + y**2) * (1 + noise)

        return {
            "experiment": "autonomous_test",
            "parameters": params,
            "result": result
        }

    def run_cycle(self, n=10):
        """
        Run multiple automated experiments
        """
        jobs = []

        for _ in range(n):

            params = self.generate_hypothesis()

            job_id = self.cluster.submit_job(
                self.experiment,
                params
            )

            jobs.append(job_id)

        return jobs
