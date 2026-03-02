import numpy as np
import time

def orbital_harmonic_force():

    t = time.time() / 86400.0

    solar_rotation = np.cos(2*np.pi*t/27)
    lunar_nodal = 0.5*np.cos(2*np.pi*t/29.5)
    long_cycle = 0.1*np.cos(2*np.pi*t/(365*1000))

    return solar_rotation + lunar_nodal + long_cycle
