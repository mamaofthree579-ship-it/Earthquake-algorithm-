import numpy as np

class HarmonicStressSolver:

    def __init__(self,
                 diffusion=0.2,
                 damping=0.3,
                 fracture_coeff=0.02):

        self.D = diffusion
        self.lambda_d = damping
        self.kappa = fracture_coeff

        self.field = np.random.normal(0,0.005,(90,180))

    def laplacian(self, F):

        return (
            np.roll(F,1,0) +
            np.roll(F,-1,0) +
            np.roll(F,1,1) +
            np.roll(F,-1,1) -
            4*F
        )

    def step(self, forcing=0.0):

        lap = self.laplacian(self.field)

        nonlinear = self.kappa * self.field**3
        noise = 0.02 * np.random.randn(*self.field.shape)

        self.field += 0.01 * (
            self.D * lap
            - self.lambda_d * self.field
            + nonlinear
            + forcing
            + noise
        )

        return self.field
