import uuid
from concurrent.futures import ThreadPoolExecutor
from core.artifact_ledger import ArtifactLedger
from core.reproducibility_engine import ReproducibilityEngine

class ClusterOrchestrator:

    def __init__(self, workers=4):
        self.executor = ThreadPoolExecutor(max_workers=workers)
        self.jobs = {}
        self.ledger = ArtifactLedger()
        self.repro = ReproducibilityEngine(self.ledger)

    def submit_job(self, func, params):

        job_id = str(uuid.uuid4())

        experiment_hash = self.repro.hash_experiment(func, params)

        future = self.executor.submit(self._run_job, job_id, func, params)

        self.jobs[job_id] = {
            "future": future,
            "status": "running",
            "hash": experiment_hash
        }

        return job_id

    def _run_job(self, job_id, func, params):

        result = func(**params)

        self.jobs[job_id]["status"] = "complete"

        artifact_id = self.ledger.store_artifact(
            job_id,
            result,
            self.jobs[job_id]["hash"]
        )

        return artifact_id

    def job_status(self, job_id):

        job = self.jobs.get(job_id)

        if not job:
            return "unknown"

        if job["future"].done():
            return "complete"

        return "running"
