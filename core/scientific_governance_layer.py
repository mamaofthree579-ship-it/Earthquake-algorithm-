import numpy as np
import hashlib


class ScientificKnowledgeGovernanceLayer:

    def __init__(self):

        self.governance_history = []

    # --------------------------------------------------
    # Dataset Structural Stability Score
    # --------------------------------------------------

    def dataset_stability_score(self, df):

        if df is None or df.empty:
            return 0.0

        try:
            numeric_cols = df.select_dtypes(include=[np.number])

            variance_score = float(
                np.mean(np.var(numeric_cols.values, axis=0))
            )

            return float(1 / (1 + variance_score))

        except Exception:
            return 0.0

    # --------------------------------------------------
    # Result Coherence Score
    # --------------------------------------------------

    def result_coherence_score(self, result):

        try:
            if result is None:
                return 0.0

            result_bytes = str(result).encode()
            hash_val = hashlib.sha256(result_bytes).hexdigest()

            entropy_score = int(hash_val[:8], 16) / 0xFFFFFFFF

            return float(entropy_score)

        except Exception:
            return 0.0

    # --------------------------------------------------
    # Governance Integrity Evaluation
    # --------------------------------------------------

    def evaluate_governance(self, df, result):

        dataset_score = self.dataset_stability_score(df)
        coherence_score = self.result_coherence_score(result)

        governance_index = float(
            0.6 * dataset_score +
            0.4 * coherence_score
        )

        record = {
            "dataset_stability": dataset_score,
            "coherence_score": coherence_score,
            "governance_index": governance_index
        }

        self.governance_history.append(record)

        return record
