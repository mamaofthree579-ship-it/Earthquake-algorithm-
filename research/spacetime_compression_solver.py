import numpy as np


class SpacetimeCompressionSolver:

    def __init__(
        self,
        grid_size=64,
        diffusion_coeff=0.1,
        compression_strength=0.05,
        noise_level=0.01
    ):

        self.grid_size = grid_size
        self.D = diffusion_coeff
        self.lambda_c = compression_strength
        self.noise_level = noise_level

        # Initialize compression field
        self.field = np.random.randn(grid_size, grid_size)

    # -----------------------------------
    # Laplacian Operator (Finite Difference)
    # -----------------------------------

    def laplacian(self, F):

        return (
            np.roll(F, 1, axis=0) +
            np.roll(F, -1, axis=0) +
            np.roll(F, 1, axis=1) +
            np.roll(F, -1, axis=1) -
            4 * F
        )

    # -----------------------------------
    # Field Evolution Step
    # -----------------------------------

    def step(self):

        grad = np.gradient(self.field)

        grad_norm_sq = grad[0]**2 + grad[1]**2

        diffusion_term = self.D * self.laplacian(self.field)

        compression_term = -self.lambda_c * grad_norm_sq

        noise_term = self.noise_level * np.random.randn(
            self.grid_size,
            self.grid_size
        )

        self.field += diffusion_term + compression_term + noise_term

        return self.field

    # -----------------------------------
    # Run Simulation
    # -----------------------------------

    def simulate(self, steps=100):

        history = []

        for _ in range(steps):
            state = self.step()
            history.append(state.copy())

        return history
