import random

class TaskScheduler:
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator

    def schedule(self):
        for job_id, job in self.orchestrator.jobs.items():
            if job["status"] == "queued":
                available_nodes = list(self.orchestrator.nodes.keys())
                if available_nodes:
                    node = random.choice(available_nodes)
                    self.orchestrator.assign_job(job_id, node)
