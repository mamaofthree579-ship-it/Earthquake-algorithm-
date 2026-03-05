import json
import hashlib
import os
from datetime import datetime

class ArtifactLedger:

    def __init__(self, path="artifacts"):
        self.path = path
        os.makedirs(self.path, exist_ok=True)

    def _generate_hash(self, artifact):
        serialized = json.dumps(artifact, sort_keys=True).encode()
        return hashlib.sha256(serialized).hexdigest()

    def record(self, job_id, job_data):

        artifact = {
            "job_id": job_id,
            "timestamp": datetime.utcnow().isoformat(),
            "node": job_data.get("node"),
            "status": job_data.get("status"),
            "result": job_data.get("result"),
        }

        artifact_hash = self._generate_hash(artifact)
        artifact["artifact_hash"] = artifact_hash

        filepath = os.path.join(self.path, f"{job_id}.json")

        with open(filepath, "w") as f:
            json.dump(artifact, f, indent=4)

        return artifact_hash

    def load_all(self):

        records = []

        for file in os.listdir(self.path):
            if file.endswith(".json"):
                with open(os.path.join(self.path, file)) as f:
                    records.append(json.load(f))

        return records
