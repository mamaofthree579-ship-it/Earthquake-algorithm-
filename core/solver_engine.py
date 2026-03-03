import numpy as np

class ResearchSolverEngine:

    def __init__(self,
                 diffusion=0.18,
                 damping=0.25,
                 fracture=0.015):

        self.diffusion = diffusion
        self.damping = damping
        self.fracture = fracture

        self.field = np.random.normal(
            0,0.002,(90,180)
        )

    def laplacian(self, F):

        return (
            np.roll(F,1,0) +
            np.roll(F,-1,0) +
            np.roll(F,1,1) +
            np.roll(F,-1,1) -
            4*F
        )

    def step(self):

        noise = 0.01 * np.random.randn(*self.field.shape)

        self.field += 0.01 * (
            self.diffusion * self.laplacian(self.field)
            - self.damping * self.field
            + self.fracture * self.field**3
            + noise
        )

        return self.field
