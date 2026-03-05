import uuid
from core.artifact_ledger import ArtifactLedger


class ClusterOrchestrator:

    def __init__(self):

        self.jobs = {}
        self.ledger = ArtifactLedger()

    def submit_job(self, func, *args, **kwargs):

        job_id = str(uuid.uuid4())

        try:

            result = func(*args, **kwargs)

            artifact_id = self.ledger.record(result)

            self.jobs[job_id] = {
                "status": "complete",
                "artifact": artifact_id
            }

        except Exception as e:

            self.jobs[job_id] = {
                "status": "failed",
                "error": str(e)
            }

        return job_id

    def get_status(self, job_id):

        return self.jobs.get(job_id, {"status": "unknown"})
