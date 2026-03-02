import numpy as np

def compute_energy(field,
                   diffusion_coeff=0.2,
                   damping_coeff=0.3,
                   fracture_coeff=0.02):

    grad_x = np.gradient(field, axis=0)
    grad_y = np.gradient(field, axis=1)

    gradient_energy = 0.5 * diffusion_coeff * (
        grad_x**2 + grad_y**2
    ).mean()

    quadratic_energy = 0.5 * damping_coeff * np.mean(field**2)
    fracture_energy = -0.25 * fracture_coeff * np.mean(field**4)

    return gradient_energy + quadratic_energy + fracture_energy
