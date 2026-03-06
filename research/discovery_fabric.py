import numpy as np

class AutonomousDiscoveryAI:

    def analyze(self, df):

        if df.empty:
            return {"status": "no_data"}

        anomaly_score = float(np.max(df["magnitude"]))

        return {
            "largest_event_detected": anomaly_score
        }
