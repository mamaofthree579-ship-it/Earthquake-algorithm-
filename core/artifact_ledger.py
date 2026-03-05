import hashlib
import json
import os

class ArtifactLedger:

    def __init__(self, path="artifacts"):

        self.path = path
        os.makedirs(path, exist_ok=True)

    def store_artifact(self, job_id, result, experiment_hash):

        artifact = {
            "job_id": job_id,
            "result": result,
            "experiment_hash": experiment_hash
        }

        data = json.dumps(artifact).encode()

        artifact_id = hashlib.sha256(data).hexdigest()

        with open(f"{self.path}/{artifact_id}.json", "w") as f:
            json.dump(artifact, f, indent=2)

        return artifact_id

    def list_artifacts(self):

        return os.listdir(self.path)
