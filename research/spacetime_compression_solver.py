import numpy as np

class SpacetimeCompressionSolver:

    def compute(self, df):

        if df.empty:
            return {"status": "no_data"}

        magnitudes = df["magnitude"].values

        compression_index = float(np.std(magnitudes))

        return {
            "compression_index": compression_index
        }
