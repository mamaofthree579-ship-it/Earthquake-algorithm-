import numpy as np

def generate_spherical_grid(n_lat=90, n_lon=180):
    lat = np.linspace(-90, 90, n_lat)
    lon = np.linspace(-180, 180, n_lon)
    lat_grid, lon_grid = np.meshgrid(lat, lon)
    return lat_grid, lon_grid
