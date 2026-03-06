import hashlib
import json
from datetime import datetime

class ReproducibilityEngine:

    def __init__(self):
        pass

    def hash_dataset(self, df):

        if df is None or df.empty:
            return "empty_dataset"

        dataset_string = df.to_json()
        return hashlib.sha256(dataset_string.encode()).hexdigest()

    def hash_results(self, results):

        results_string = json.dumps(results, sort_keys=True)
        return hashlib.sha256(results_string.encode()).hexdigest()

    def create_reproducibility_record(self, df, results):

        dataset_hash = self.hash_dataset(df)
        results_hash = self.hash_results(results)

        record = {
            "timestamp": datetime.utcnow().isoformat(),
            "dataset_hash": dataset_hash,
            "results_hash": results_hash
        }

        return record
