# research/harmonic_tensor_discovery.py

import numpy as np


class HarmonicTensorDiscovery:

    def discover(self, df):

        if df.empty:
            return {"status": "no_data"}

        magnitudes = df["magnitude"].values

        tensor_value = np.mean(magnitudes) * np.std(magnitudes)

        return {
            "tensor_signature": float(tensor_value),
            "samples": len(magnitudes)
        }
