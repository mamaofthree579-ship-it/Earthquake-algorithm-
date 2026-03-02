import numpy as np

def spherical_laplacian(field, dtheta, dphi):
    lap = np.zeros_like(field)

    lap[1:-1,1:-1] = (
        (field[2:,1:-1] - 2*field[1:-1,1:-1] + field[:-2,1:-1]) / dtheta**2
        +
        (field[1:-1,2:] - 2*field[1:-1,1:-1] + field[1:-1,:-2]) / dphi**2
    )

    return lap


def run_simulation(n_lat=90, n_lon=180, steps=200, dt=0.01,
                   D=0.2, lam=0.3, kappa=0.02,
                   celestial_amp=1.0, noise_amp=0.05):

    stress = np.random.normal(0, 0.01, (n_lat, n_lon))

    dtheta = np.pi / n_lat
    dphi = 2*np.pi / n_lon

    for t in range(steps):

        lap = spherical_laplacian(stress, dtheta, dphi)

        # Celestial harmonic forcing
        celestial_force = celestial_amp * np.cos(2*np.pi*t/27)

        nonlinear = kappa * stress**3
        noise = noise_amp * np.random.randn(n_lat, n_lon)

        stress = stress + dt * (
            D * lap
            - lam * stress
            + nonlinear
            + celestial_force
            + noise
        )

    return stress
