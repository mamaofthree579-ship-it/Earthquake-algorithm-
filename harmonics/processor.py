"""
Harmonics & signal processing helpers.
- demo_harmonics_plot: creates a synthetic signal and plots FFT using Streamlit.
- real functions should accept time-series arrays and return frequency-domain features.
"""
import numpy as np
import streamlit as st
from scipy import fftpack
import pandas as pd

def demo_harmonics_plot(n=2048):
    t = np.linspace(0, 1.0, n)
    tectonic = 0.6 * np.sin(2 * np.pi * 2 * t)        # low-frequency component
    solar = 0.25 * np.sin(2 * np.pi * 60 * t)         # high-frequency component
    noise = 0.05 * np.random.randn(len(t))
    signal = tectonic + solar + noise

    yf = fftpack.fft(signal)
    xf = np.linspace(0.0, 1.0/(2.0*(t[1]-t[0])), n//2)
    amp = 2.0/n * np.abs(yf[:n//2])
    df = pd.DataFrame({"freq": xf, "amp": amp})
    st.line_chart(df.set_index("freq")["amp"].iloc[:400])
