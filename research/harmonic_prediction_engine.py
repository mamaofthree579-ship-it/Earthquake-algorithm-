import numpy as np

class HarmonicPredictionEngine:

    def analyze(self, df):

        if df.empty:
            return {"status": "no_data"}

        magnitudes = df["magnitude"].values

        harmonic_score = float(np.mean(magnitudes))

        return {
            "harmonic_mean": harmonic_score,
            "events_analyzed": len(magnitudes)
        }
