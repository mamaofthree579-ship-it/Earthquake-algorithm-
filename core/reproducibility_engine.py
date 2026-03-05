import hashlib
import inspect
import json

class ReproducibilityEngine:

    def __init__(self, ledger):

        self.ledger = ledger

    def hash_experiment(self, func, params):

        source = inspect.getsource(func)

        data = {
            "code": source,
            "params": params
        }

        serialized = json.dumps(data, sort_keys=True).encode()

        return hashlib.sha256(serialized).hexdigest()

    def verify_artifact(self, artifact):

        return artifact["experiment_hash"]
