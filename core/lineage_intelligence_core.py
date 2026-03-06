import hashlib
import json
from datetime import datetime


class LineageIntelligenceCore:

    def __init__(self):
        self.lineage_registry = {}

    # -----------------------------------------
    # Dataset Hashing
    # -----------------------------------------

    def hash_dataset(self, df):

        if df is None or df.empty:
            return "empty_dataset"

        dataset_json = df.to_json()

        return hashlib.sha256(
            dataset_json.encode()
        ).hexdigest()

    # -----------------------------------------
    # Result Hashing
    # -----------------------------------------

    def hash_result(self, result):

        result_json = json.dumps(result, sort_keys=True)

        return hashlib.sha256(
            result_json.encode()
        ).hexdigest()

    # -----------------------------------------
    # Register Experiment Lineage
    # -----------------------------------------

    def register_experiment(self, df, parameters, result):

        lineage_id = hashlib.sha256(
            str(datetime.utcnow()).encode()
        ).hexdigest()

        record = {
            "timestamp": datetime.utcnow().isoformat(),
            "dataset_hash": self.hash_dataset(df),
            "parameter_hash": self.hash_result(parameters),
            "result_hash": self.hash_result(result),
            "parameters": parameters,
            "result_preview": result
        }

        self.lineage_registry[lineage_id] = record

        return lineage_id

    # -----------------------------------------
    # Query Lineage Registry
    # -----------------------------------------

    def list_lineage(self):

        return self.lineage_registry
