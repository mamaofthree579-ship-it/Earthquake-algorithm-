import numpy as np

def celestial_forcing(t):
    solar_rot = np.cos(2*np.pi*t/27)
    lunar_cycle = 0.5*np.cos(2*np.pi*t/29.5)
    return solar_rot + lunar_cycle
