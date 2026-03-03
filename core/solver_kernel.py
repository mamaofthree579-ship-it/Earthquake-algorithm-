import numpy as np

class SolverKernel:

    def __init__(self, grid_shape=(180, 360)):

        self.field = np.random.normal(
            0, 0.001, grid_shape
        )

        self.diffusion = 0.15
        self.damping = 0.25

    def laplacian(self, F):

        return (
            np.roll(F, 1, 0) +
            np.roll(F, -1, 0) +
            np.roll(F, 1, 1) +
            np.roll(F, -1, 1) -
            4 * F
        )

    def step(self):

        noise = 0.001 * np.random.randn(*self.field.shape)

        self.field += 0.01 * (
            self.diffusion * self.laplacian(self.field)
            - self.damping * self.field
            + noise
        )

        return self.field
