import numpy as np
from models.spherical_pde import run_simulation

def run_ensemble(runs=20):

    results = []

    for i in range(runs):
        stress = run_simulation(
            celestial_amp=np.random.uniform(0.5,1.5),
            noise_amp=np.random.uniform(0.03,0.1)
        )
        results.append(stress)

    results = np.array(results)

    threshold = 2.0
    probability_map = np.mean(results > threshold, axis=0)

    return probability_map
