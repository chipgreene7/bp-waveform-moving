import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time

# App config
st.set_page_config(layout="wide")
st.title("🫀 Real-Time ECG + ABP Waveform Simulator")

# Sidebar settings
st.sidebar.header("Simulation Settings")
ecg_rhythm = st.sidebar.selectbox("Select ECG Rhythm", [
    "Normal Sinus Rhythm", "Atrial Fibrillation", "Atrial Flutter",
    "Ventricular Tachycardia", "Ventricular Fibrillation",
    "Sinus Bradycardia", "Supraventricular Tachycardia (SVT)",
    "Asystole", "Sinus Tachycardia"
])

systolic = st.sidebar.slider("Systolic BP (mmHg)", 20, 200, 120)
diastolic = st.sidebar.slider("Diastolic BP (mmHg)", 10, 130, 80)
map_val = round((systolic + 2 * diastolic) / 3, 1)
st.sidebar.markdown(f"**MAP:** {map_val} mmHg")

start_sim = st.sidebar.toggle("Start Simulation")

# Time settings
fs = 500  # samples per second
duration = 2  # seconds per window
t = np.linspace(0, duration, duration * fs)

# ECG waveform generators
def generate_ecg(rhythm, t):
    if rhythm == "Normal Sinus Rhythm":
        return 0.6 * np.sin(2 * np.pi * 1.0 * t) * (np.square(np.sin(2*np.pi*1.0*t)) > 0.5)
    elif rhythm == "Atrial Fibrillation":
        return 0.2 * np.random.randn(len(t))
    elif rhythm == "Atrial Flutter":
        return 0.4 * np.sin(2 * np.pi * 4 * t)
    elif rhythm == "Ventricular Tachycardia":
        return 0.9 * np.sin(2 * np.pi * 3 * t)
    elif rhythm == "Ventricular Fibrillation":
        return 0.7 * np.random.randn(len(t))
    elif rhythm == "Sinus Bradycardia":
        return 0.6 * np.sin(2 * np.pi * 0.5 * t) * (np.square(np.sin(2*np.pi*0.5*t)) > 0.5)
    elif rhythm == "Supraventricular Tachycardia (SVT)":
        return 0.5 * np.sin(2 * np.pi * 5 * t)
    elif rhythm == "Asystole":
        return np.zeros_like(t)
    elif rhythm == "Sinus Tachycardia":
        return 0.6 * np.sin(2 * np.pi * 2 * t) * (np.square(np.sin(2*np.pi*2*t)) > 0.5)
    else:
        return np.zeros_like(t)

# ABP waveform generator
def generate_abp(t, systolic=120, diastolic=80):
    freq = 1.0  # 60 bpm
    waveform = (np.sin(2 * np.pi * freq * t - 0.3)**15) * (systolic - diastolic) + diastolic
    waveform = np.clip(waveform, diastolic, systolic)
    return waveform

# Live plotting
ecg_placeholder = st.empty()

def plot_signals(t, ecg_signal, abp_signal):
    fig, ax = plt.subplots(2, 1, figsize=(10, 4), sharex=True)
    
    ax[0].plot(t, ecg_signal, color='red')
    ax[0].set_ylabel("ECG (mV)")
    ax[0].set_ylim(-1, 1)
    ax[0].grid(True)

    ax[1].plot(t, abp_signal, color='blue')
    ax[1].set_ylabel("ABP (mmHg)")
    ax[1].set_ylim(0, 200)
    ax[1].set_xlabel("Time (s)")
    ax[1].grid(True)

    plt.tight_layout()
    return fig

# Simulation loop
if start_sim:
    while start_sim:
        ecg_signal = generate_ecg(ecg_rhythm, t)
        abp_signal = generate_abp(t, systolic, diastolic)
        fig = plot_signals(t, ecg_signal, abp_signal)
        ecg_placeholder.pyplot(fig)
        time.sleep(duration)
        start_sim = st.sidebar.toggle("Start Simulation", value=True, key="run")
else:
    st.info("Click 'Start Simulation' to begin real-time ECG and ABP waveform display.")
