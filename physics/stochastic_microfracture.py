import numpy as np

def microfracture_noise(field,
                        base_sigma=0.05,
                        stress_threshold=1.5):

    stress = np.abs(field)

    amplification = np.where(
        stress > stress_threshold,
        2.0,
        1.0
    )

    return base_sigma * amplification * np.random.randn(*field.shape)
