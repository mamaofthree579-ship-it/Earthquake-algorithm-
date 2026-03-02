import numpy as np

def monte_carlo_solver(solver, runs=100):
    results = []
    for i in range(runs):
        result = solver(noise_amp=np.random.uniform(0.05,0.2))
        results.append(result)
    return np.array(results)
