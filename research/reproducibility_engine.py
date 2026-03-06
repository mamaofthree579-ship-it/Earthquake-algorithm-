# core/reproducibility_engine.py

import hashlib
import json
from datetime import datetime


class ReproducibilityEngine:
    """
    Generates reproducible experiment hashes and metadata
    so scientific results can always be verified.
    """

    def __init__(self):
        pass

    def create_reproducibility_record(self, payload):

        record = {
            "timestamp": str(datetime.utcnow()),
            "payload": payload
        }

        serialized = json.dumps(record, sort_keys=True)

        record_hash = hashlib.sha256(serialized.encode()).hexdigest()

        return {
            "record": record,
            "hash": record_hash
        }
