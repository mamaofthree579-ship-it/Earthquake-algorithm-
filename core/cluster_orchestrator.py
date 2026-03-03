import uuid
from datetime import datetime

class ClusterOrchestrator:
    def __init__(self):
        self.nodes = {}
        self.jobs = {}

    def register_node(self, node_id: str):
        self.nodes[node_id] = {
            "status": "active",
            "last_heartbeat": datetime.utcnow()
        }

    def submit_job(self, job_payload: dict):
        job_id = str(uuid.uuid4())
        self.jobs[job_id] = {
            "payload": job_payload,
            "status": "queued",
            "created_at": datetime.utcnow()
        }
        return job_id

    def assign_job(self, job_id: str, node_id: str):
        if job_id in self.jobs and node_id in self.nodes:
            self.jobs[job_id]["status"] = "assigned"
            self.jobs[job_id]["node"] = node_id
            return True
        return False

    def update_status(self, job_id: str, status: str):
        if job_id in self.jobs:
            self.jobs[job_id]["status"] = status
