import numpy as np

def compute_stability_index(magnitude_series):

    if len(magnitude_series) == 0:
        return 1.0

    variance = np.var(magnitude_series)

    return 1 / (1 + variance)
