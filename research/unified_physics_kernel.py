import numpy as np


class UnifiedPhysicsKernel:

    def __init__(self,
                 harmonic_engine,
                 compression_solver,
                 tensor_engine):

        self.harmonic_engine = harmonic_engine
        self.compression_solver = compression_solver
        self.tensor_engine = tensor_engine

        self.history = []

    # -----------------------------------------
    # Unified Simulation Execution
    # -----------------------------------------

    def run_simulation(self, df, time_index=0):

        if df is None or df.empty:
            return {"status": "no_data"}

        # Harmonic signal
        harmonic_score = self.harmonic_engine.analyze(df)

        # Compression field
        compression_score = self.compression_solver.compute(df)

        # Tensor structure
        tensor_score = self.tensor_engine.discover(df)

        # Aggregate stability metric
        stability_index = np.mean([
            float(harmonic_score.get("harmonic_mean", 0)),
            float(compression_score.get("compression_index", 0)),
            float(tensor_score.get("tensor_field_strength", 0))
        ])

        result = {
            "unified_stability_index": float(stability_index),
            "components": {
                "harmonic": harmonic_score,
                "compression": compression_score,
                "tensor": tensor_score
            }
        }

        self.history.append(result)

        return result
