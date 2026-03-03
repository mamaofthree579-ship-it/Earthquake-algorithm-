import time
from research.reproducibility_engine import ReproducibilityEngine

class MeshRuntime:
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.repro_engine = ReproducibilityEngine()

    def execute(self, job_id: str):
        job = self.orchestrator.jobs.get(job_id)
        if not job:
            return

        self.orchestrator.update_status(job_id, "running")

        result = job["payload"]["compute"]()

        hash_result = self.repro_engine.hash_result(result)

        self.orchestrator.jobs[job_id]["result"] = result
        self.orchestrator.jobs[job_id]["hash"] = hash_result

        self.orchestrator.update_status(job_id, "completed")
