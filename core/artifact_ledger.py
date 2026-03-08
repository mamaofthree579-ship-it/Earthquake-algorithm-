import os
import pandas as pd

class ArtifactLedger:

    def __init__(self, storage_path="research_artifacts/ledger.csv"):
        self.storage_path = storage_path

        os.makedirs(os.path.dirname(storage_path), exist_ok=True)

        if not os.path.exists(storage_path):
            pd.DataFrame().to_csv(storage_path, index=False)

    # -------------------------

    def save_dataframe(self, df):

        if df is None or df.empty:
            return

        df.to_csv(
            self.storage_path,
            mode="a",
            header=not os.path.exists(self.storage_path),
            index=False
        )

    # -------------------------

    def load_dataframe(self):

        try:
            return pd.read_csv(self.storage_path)
        except Exception:
            return pd.DataFrame()
