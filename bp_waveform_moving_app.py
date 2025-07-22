
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# Set page configuration
st.set_page_config(page_title="ABP Waveform Simulator", layout="wide")

# Sidebar controls
st.sidebar.header("Simulation Parameters")
systolic = st.sidebar.slider("Systolic Pressure (mmHg)", 80, 200, 120)
diastolic = st.sidebar.slider("Diastolic Pressure (mmHg)", 40, 120, 80)
heart_rate = st.sidebar.slider("Heart Rate (bpm)", 40, 180, 75)
duration = st.sidebar.slider("Duration (seconds)", 5, 60, 30)

# Sampling frequency
fs = 1000  # Hz

# Function to generate one ABP beat waveform
def generate_beat_waveform():
    cycle_duration = 60 / heart_rate
    t_beat = np.linspace(0, cycle_duration, int(fs * cycle_duration))
    upstroke = 1 / (1 + np.exp(-50 * (t_beat - 0.2 * cycle_duration)))
    notch = -0.1 * np.exp(-((t_beat - 0.5 * cycle_duration) ** 2) / (2 * (0.015 * cycle_duration) ** 2))
    decay = np.exp(-3 * t_beat / cycle_duration)
    wave = upstroke + notch + decay
    wave = (wave - wave.min()) / (wave.max() - wave.min())
    return diastolic + wave * (systolic - diastolic)

# Generate full waveform for the specified duration
samples_per_beat = int(fs * (60 / heart_rate))
total_samples = int(fs * duration)
waveform = np.zeros(total_samples)

for i in range(0, total_samples, samples_per_beat):
    beat_wave = generate_beat_waveform()
    end_idx = min(i + samples_per_beat, total_samples)
    waveform[i:end_idx] = beat_wave[:end_idx - i]

# Time axis
t = np.linspace(0, duration, total_samples)

# Plot the waveform
fig, ax = plt.subplots(figsize=(12, 4))
ax.plot(t, waveform, color='red')
ax.set_title("Simulated Arterial Blood Pressure Waveform")
ax.set_xlabel("Time (s)")
ax.set_ylabel("Pressure (mmHg)")
ax.set_ylim(30, 140)
ax.set_xlim(0, duration)
ax.grid(True)

# Display in Streamlit
st.pyplot(fig)

