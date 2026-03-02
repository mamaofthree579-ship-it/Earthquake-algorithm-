import numpy as np
import time

def celestial_forcing():
    t = time.time() / 86400.0  # days
    
    solar_rot = np.cos(2*np.pi*t/27)
    lunar_cycle = 0.5*np.cos(2*np.pi*t/29.5)
    precession = 0.1*np.cos(2*np.pi*t/(26000*365))
    
    return solar_rot + lunar_cycle + precession
