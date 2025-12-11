import streamlit as st
from harmonics.processor import demo_harmonics_plot
import numpy as np
import pandas as pd
from scipy import fftpack

st.title("Harmonics Lab")

st.write("Interactive harmonics demo — synthesize and analyze signals")

n = st.slider("Samples (n)", 512, 8192, 2048, step=256)
freq_low = st.slider("Low-frequency (Hz)", 0.1, 10.0, 2.0)
freq_high = st.slider("High-frequency (Hz)", 10.0, 200.0, 60.0)
amp_low = st.slider("Low-frequency amplitude", 0.0, 2.0, 0.6)
amp_high = st.slider("High-frequency amplitude", 0.0, 1.0, 0.25)
noise_level = st.slider("Noise std", 0.0, 0.5, 0.05)

t = np.linspace(0, 1.0, n)
signal = amp_low * np.sin(2 * np.pi * freq_low * t) + amp_high * np.sin(2 * np.pi * freq_high * t) + noise_level * np.random.randn(n)
yf = fftpack.fft(signal)
xf = np.linspace(0.0, 1.0/(2.0*(t[1]-t[0])), n//2)
amp = 2.0/n * np.abs(yf[:n//2])
df = pd.DataFrame({"freq": xf, "amp": amp})
st.line_chart(df.set_index("freq")["amp"].iloc[:400])
st.write("Preview of time-series (first 100 samples):")
st.line_chart(signal[:100])
