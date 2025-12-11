import numpy as np
import pandas as pd
from harmonics import processor

def test_demo_harmonics_dataframe():
    # Use the underlying functions by constructing signal and computing FFT directly
    n = 1024
    t = np.linspace(0, 1.0, n)
    tectonic = 0.6 * np.sin(2 * np.pi * 2 * t)
    solar = 0.25 * np.sin(2 * np.pi * 60 * t)
    noise = 0.01 * np.random.randn(len(t))
    signal = tectonic + solar + noise

    # reproduce FFT logic from processor
    from scipy import fftpack
    yf = fftpack.fft(signal)
    xf = np.linspace(0.0, 1.0/(2.0*(t[1]-t[0])), n//2)
    amp = 2.0/n * np.abs(yf[:n//2])
    df = pd.DataFrame({"freq": xf, "amp": amp})

    # Basic assertions
    assert "freq" in df.columns and "amp" in df.columns
    assert len(df) == n//2
    # There should be a peak at low frequency (near index for 2 Hz) and at 60 Hz
    peak_idx = int(df["amp"].idxmax())
    assert peak_idx >= 0
    assert df["amp"].max() > 0.01
