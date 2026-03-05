import json
import os
import uuid
from datetime import datetime


class ArtifactLedger:

    def __init__(self, path="artifacts"):

        self.path = path

        if not os.path.exists(self.path):
            os.makedirs(self.path)

    def record(self, data):

        artifact_id = str(uuid.uuid4())

        artifact = {
            "artifact_id": artifact_id,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data
        }

        filename = os.path.join(self.path, f"{artifact_id}.json")

        with open(filename, "w") as f:
            json.dump(artifact, f, indent=2)

        return artifact_id

    def list_artifacts(self):

        files = os.listdir(self.path)

        return files
