import numpy as np


class CivilizationKnowledgeEvolutionSimulator:

    def __init__(self):

        # Evolution coefficients
        self.discovery_rate = 0.4
        self.communication_rate = 0.3
        self.stability_rate = 0.2
        self.noise_scale = 0.1

        self.history = []

    # -----------------------------
    # Discovery Emergence Field
    # -----------------------------

    def discovery_field(self, state):

        gradient = np.gradient(state)

        return np.mean(np.abs(gradient))

    # -----------------------------
    # Communication Diffusion Field
    # -----------------------------

    def communication_field(self, state):

        return np.std(state)

    # -----------------------------
    # Stability Preservation Field
    # -----------------------------

    def stability_field(self, state):

        return np.mean(state)

    # -----------------------------
    # Civilization Evolution Step
    # -----------------------------

    def evolve(self, state_vector):

        state = np.array(state_vector)

        D = self.discovery_field(state)
        C = self.communication_field(state)
        S = self.stability_field(state)

        noise = np.random.normal(0, self.noise_scale, size=state.shape)

        next_state = (
            state +
            self.discovery_rate * D +
            self.communication_rate * C -
            self.stability_rate * S +
            noise
        )

        self.history.append(next_state)

        return next_state

    # -----------------------------
    # Multi-Step Evolution Simulation
    # -----------------------------

    def simulate(self, initial_state, steps=50):

        state = np.array(initial_state)

        trajectory = []

        for _ in range(steps):
            state = self.evolve(state)
            trajectory.append(state.copy())

        return trajectory
