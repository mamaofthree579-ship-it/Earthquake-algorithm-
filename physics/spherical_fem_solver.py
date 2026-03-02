import numpy as np

class SphericalFEMSolver:

    def __init__(self,
                 n_lat=90,
                 n_lon=180,
                 diffusion=0.2,
                 damping=0.3,
                 fracture_coeff=0.02):

        self.n_lat = n_lat
        self.n_lon = n_lon
        self.D = diffusion
        self.lambda_d = damping
        self.kappa = fracture_coeff

        self.field = np.random.normal(
            0, 0.01,
            (n_lat, n_lon)
        )

    def laplacian(self, F):

        lap = np.zeros_like(F)

        lap[1:-1,1:-1] = (
            (F[2:,1:-1] - 2*F[1:-1,1:-1] + F[:-2,1:-1])
            +
            (F[1:-1,2:] - 2*F[1:-1,1:-1] + F[1:-1,:-2])
        )

        return lap

    def step(self, forcing=0.0, noise_amp=0.05, dt=0.01):

        lap = self.laplacian(self.field)

        nonlinear = self.kappa * self.field**3
        noise = noise_amp * np.random.randn(*self.field.shape)

        self.field += dt * (
            self.D * lap
            - self.lambda_d * self.field
            + nonlinear
            + forcing
            + noise
        )

        return self.field
