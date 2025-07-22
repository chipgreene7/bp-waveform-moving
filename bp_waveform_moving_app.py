
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

# Generate one heartbeat waveform with dicrotic notch
def generate_beat_waveform():
    t = np.linspace(0, cycle_duration, int(fs * cycle_duration))
    # Simulate systolic upstroke
    upstroke = np.exp(-((t - 0.15 * cycle_duration) ** 2) / (2 * (0.02 * cycle_duration) ** 2))
    # Simulate dicrotic notch
    notch = -0.2 * np.exp(-((t - 0.4 * cycle_duration) ** 2) / (2 * (0.01 * cycle_duration) ** 2))
    # Simulate diastolic decay
    decay = np.exp(-2 * t / cycle_duration)
    wave = upstroke + notch + decay
    wave = (wave - wave.min()) / (wave.max() - wave.min())
    return diastolic + wave * (systolic - diastolic)

# Initialize buffer
waveform_buffer = np.full(buffer_size, diastolic)
time_buffer = np.linspace(-window_duration, 0, buffer_size)

# Placeholder for plot
plot_placeholder = st.empty()

# Live update loop
if st.session_state.running:
    beat_wave = generate_beat_waveform()
    beat_index = 0
    while st.session_state.running:
        if beat_index >= len(beat_wave):
            beat_wave = generate_beat_waveform()
            beat_index = 0

        sample = beat_wave[beat_index]
        beat_index += 1

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

