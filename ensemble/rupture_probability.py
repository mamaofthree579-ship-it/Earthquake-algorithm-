import numpy as np

def rupture_probability(ensemble_fields,
                        threshold=2.0):

    ensemble_fields = np.array(ensemble_fields)

    return np.mean(
        np.abs(ensemble_fields) > threshold,
        axis=0
    )
