import numpy as np

class HarmonicTensorDiscovery:

    def discover(self, df):

        if df.empty:
            return {"status": "no_data"}

        tensor_strength = float(np.var(df["magnitude"]))

        return {
            "tensor_field_strength": tensor_strength
        }
