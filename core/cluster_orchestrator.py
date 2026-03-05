import uuid
from core.artifact_ledger import ArtifactLedger

class ClusterOrchestrator:

    def __init__(self):
        self.jobs = {}
        self.ledger = ArtifactLedger()

    def submit_job(self, func, params):

        job_id = str(uuid.uuid4())

        self.jobs[job_id] = "running"

        result = func(params)

        artifact_id = self.ledger.save(result)

        self.jobs[job_id] = "completed"

        return job_id

    def job_status(self, job_id):

        return self.jobs.get(job_id, "unknown")
