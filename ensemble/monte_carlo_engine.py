import numpy as np

def monte_carlo_risk_simulation(field, runs=50):

    ensemble = []

    for _ in range(runs):

        perturbation = field + 0.01 * np.random.randn(*field.shape)
        ensemble.append(np.mean(np.abs(perturbation)))

    return np.mean(ensemble)
