import hashlib
import json

class ReproducibilityEngine:
    def hash_result(self, result):
        encoded = json.dumps(result, sort_keys=True).encode()
        return hashlib.sha256(encoded).hexdigest()
