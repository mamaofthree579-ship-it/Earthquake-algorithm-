import hashlib
import json


class ReproducibilityEngine:

    def __init__(self, orchestrator, ledger):
        self.orchestrator = orchestrator
        self.ledger = ledger

    def _hash_result(self, result):

        serialized = json.dumps(result, sort_keys=True).encode()

        return hashlib.sha256(serialized).hexdigest()

    def verify(self, artifact):

        # Extract original data
        job_id = artifact["job_id"]
        original_result = artifact["result"]
        original_hash = artifact["artifact_hash"]

        # Re-run experiment
        job = self.orchestrator.jobs.get(job_id)

        if not job:
            return {
                "verified": False,
                "reason": "Original job not found in orchestrator"
            }

        compute_fn = job["payload"]["compute"]

        new_result = compute_fn()

        new_hash = self._hash_result(new_result)

        verified = new_hash == original_hash

        return {
            "verified": verified,
            "original_hash": original_hash,
            "recomputed_hash": new_hash,
            "result": new_result
        }

    def verify_all(self):

        artifacts = self.ledger.load_all()

        reports = []

        for artifact in artifacts:

            report = self.verify(artifact)

            reports.append({
                "job_id": artifact["job_id"],
                "verified": report["verified"]
            })

        return reports
