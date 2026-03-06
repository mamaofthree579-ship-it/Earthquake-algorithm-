import uuid
import hashlib
import time
from concurrent.futures import ThreadPoolExecutor


class InstitutionalScientificRuntimeOS:

    def __init__(self, max_workers=4):

        self.executor = ThreadPoolExecutor(max_workers=max_workers)

        self.job_registry = {}
        self.artifact_store = {}

    # ---------------------------------------------
    # Execution Hashing
    # ---------------------------------------------

    def _hash_payload(self, payload):

        return hashlib.sha256(
            str(payload).encode()
        ).hexdigest()

    # ---------------------------------------------
    # Submit Scientific Job
    # ---------------------------------------------

    def submit_scientific_job(self, function, *args, **kwargs):

        job_id = str(uuid.uuid4())

        future = self.executor.submit(
            self._safe_execute,
            function,
            *args,
            **kwargs
        )

        self.job_registry[job_id] = {
            "future": future,
            "timestamp": time.time(),
            "status": "running"
        }

        return job_id

    # ---------------------------------------------
    # Safe Execution Wrapper
    # ---------------------------------------------

    def _safe_execute(self, function, *args, **kwargs):

        try:
            result = function(*args, **kwargs)

            artifact_id = self._hash_payload(result)

            self.artifact_store[artifact_id] = result

            return result

        except Exception as e:

            return {"error": str(e)}

    # ---------------------------------------------
    # Job Status Query
    # ---------------------------------------------

    def get_job_status(self, job_id):

        if job_id not in self.job_registry:
            return "unknown"

        job = self.job_registry[job_id]

        if job["future"].done():

            job["status"] = "completed"

            return "completed"

        return "running"

    # ---------------------------------------------
    # Artifact Retrieval
    # ---------------------------------------------

    def list_artifacts(self):

        return list(self.artifact_store.values())
