
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time

# Set page configuration
st.set_page_config(page_title="Live ABP Waveform", layout="wide")

# Title
st.title("🩺 Live Arterial Blood Pressure Waveform with Dicrotic Notch")

# Sidebar inputs
st.sidebar.header("Input Blood Pressure")
systolic = st.sidebar.slider("Systolic Pressure (mmHg)", 40, 200, 120)
diastolic = st.sidebar.slider("Diastolic Pressure (mmHg)", 10, 120, 80)
heart_rate = st.sidebar.slider("Heart Rate (bpm)", 40, 180, 75)

# Derived values
mean_pressure = diastolic + (systolic - diastolic) / 3
cycle_duration = 60 / heart_rate  # seconds per beat
fs = 1000  # sampling frequency
window_duration = 5  # seconds of data to display
buffer_size = int(fs * window_duration)

# Session state for control
if "running" not in st.session_state:
    st.session_state.running = False

# Start/Stop buttons
col1, col2 = st.columns(2)
with col1:
    if st.button("▶️ Start"):
        st.session_state.running = True
with col2:
    if st.button("⏹️ Stop"):
        st.session_state.running = False

# Generate one realistic ABP waveform beat
def generate_abp_waveform():
    t = np.linspace(0, cycle_duration, int(fs * cycle_duration))
    # Systolic upstroke: sharp rise
    upstroke = np.exp(-((t - 0.15 * cycle_duration) ** 2) / (2 * (0.02 * cycle_duration) ** 2))
    # Dicrotic notch: small dip
    notch = -0.2 * np.exp(-((t - 0.4 * cycle_duration) ** 2) / (2 * (0.01 * cycle_duration) ** 2))
    # Diastolic decay: exponential fall
    decay = np.exp(-3 * t / cycle_duration)
    waveform = upstroke + notch + decay
    waveform = (waveform - waveform.min()) / (waveform.max() - waveform.min())
    return diastolic + waveform * (systolic - diastolic)

# Initialize buffer
waveform_buffer = np.full(buffer_size, diastolic)
time_buffer = np.linspace(-window_duration, 0, buffer_size)

# Placeholder for plot
plot_placeholder = st.empty()

# Live update loop
while st.session_state.running:
    beat_wave = generate_abp_waveform()
    for sample in beat_wave:
        if not st.session_state.running:
            break
        waveform_buffer = np.roll(waveform_buffer, -1)
        waveform_buffer[-1] = sample
        time_buffer = np.roll(time_buffer, -1)
        time_buffer[-1] = time_buffer[-2] + 1/fs

        # Plot
        fig, ax = plt.subplots(figsize=(12, 4))
        ax.plot(time_buffer, waveform_buffer, color='red')
        ax.set_title("Live Arterial Blood Pressure Waveform")
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Pressure (mmHg)")
        ax.set_ylim(30, 220)
        ax.grid(True)
        plot_placeholder.pyplot(fig)

        time.sleep(1/fs)

