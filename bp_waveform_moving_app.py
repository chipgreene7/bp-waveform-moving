import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import time

# Page setup
st.set_page_config(layout="wide")

# --- ECG Waveform Generator ---
def synthetic_ecg(t, hr=75, rhythm="Normal"):
    beats_per_second = hr / 60.0
    r_wave_positions = np.arange(0, t[-1], 1.0 / beats_per_second)
    signal = np.zeros_like(t)
    for r in r_wave_positions:
        idx = np.argmin(np.abs(t - r))
        if rhythm == "Normal":
            signal[idx] = 1.2
            if idx + 1 < len(signal):
                signal[idx + 1] = -0.5
        elif rhythm == "AFib":
            signal[idx] = 0.3 * np.random.randn()
        elif rhythm == "V-Tach":
            signal[idx:idx + 3] = 1.0  # wide complex
    signal = np.convolve(signal, np.exp(-np.linspace(0, 2, 30)), mode='same')
    return signal

# --- ABP Waveform Generator ---
def generate_abp(t, hr=75, sys=120, dia=80):
    wave = np.zeros_like(t)
    beat_interval = 60.0 / hr
    num_beats = int(t[-1] / beat_interval)
    for i in range(num_beats):
        start = int((i * beat_interval) * len(t) / t[-1])
        end = start + int(0.3 * len(t) / t[-1])
        if end < len(t):
            peak = np.hanning(end - start)
            peak = peak**3
            wave[start:end] += peak
    wave = (wave - np.min(wave)) / (np.max(wave) - np.min(wave))
    wave = wave * (sys - dia) + dia
    return wave

# --- Plethysmographic Waveform Generator ---
def generate_pleth(t, hr=75):
    signal = 0.3 * np.sin(2 * np.pi * (hr / 60.0) * t)
    signal += 0.05 * np.sin(4 * np.pi * (hr / 60.0) * t)
    return signal

# --- Presets ---
preset_cases = {
    "Normal": {"hr": 75, "sys": 120, "dia": 80, "rhythm": "Normal"},
    "AFib RVR": {"hr": 130, "sys": 110, "dia": 70, "rhythm": "AFib"},
    "V-Tach": {"hr": 160, "sys": 80, "dia": 40, "rhythm": "V-Tach"},
    "Hypovolemic Shock": {"hr": 125, "sys": 85, "dia": 50, "rhythm": "Normal"},
    "Custom": {},
}

ecg_types = ["Normal", "AFib", "V-Tach"]

# --- Sidebar UI ---
st.sidebar.title("🩺 VitalSim Case Selector")
selected_case = st.sidebar.selectbox("Choose a Scenario", list(preset_cases.keys()))

if selected_case == "Custom":
    hr = st.sidebar.slider("Heart Rate (bpm)", 30, 180, 75)
    sys = st.sidebar.slider("Systolic BP", 60, 200, 120)
    dia = st.sidebar.slider("Diastolic BP", 30, 120, 80)
    rhythm = st.sidebar.selectbox("ECG Rhythm", ecg_types)
else:
    case = preset_cases[selected_case]
    hr = case["hr"]
    sys = case["sys"]
    dia = case["dia"]
    rhythm = case["rhythm"]

# --- Timebase ---
fs = 500
duration = 8  # seconds on screen
t = np.linspace(0, duration, duration * fs)

# --- Layout ---
col1, col2 = st.columns(2)
ecg_placeholder = col1.empty()
abp_placeholder = col2.empty()
pleth_placeholder = st.empty()

# --- Live Simulation Loop ---
for _ in range(200):
    ecg = synthetic_ecg(t, hr, rhythm)
    abp = generate_abp(t, hr, sys, dia)
    pleth = generate_pleth(t, hr)

    # ECG plot
    fig_ecg, ax = plt.subplots(figsize=(8, 2))
    ax.plot(t, ecg, color='red')
    ax.set_ylim(-1, 1.5)
    ax.axis("off")
    ax.set_title(f"ECG ({rhythm}, HR: {hr} bpm)", fontsize=12)
    ecg_placeholder.pyplot(fig_ecg)

    # ABP plot
    fig_abp, ax = plt.subplots(figsize=(8, 2))
    ax.plot(t, abp, color='blue')
    ax.set_ylim(30, 180)
    ax.axis("off")
    ax.set_title(f"ABP: {sys}/{dia} mmHg", fontsize=12)
    abp_placeholder.pyplot(fig_abp)

    # Pleth plot
    fig_pleth, ax = plt.subplots(figsize=(16, 2))
    ax.plot(t, pleth, color='green')
    ax.set_ylim(-0.6, 0.6)
    ax.axis("off")
    ax.set_title(f"SpO₂ Pleth (HR: {hr} bpm)", fontsize=12)
    pleth_placeholder.pyplot(fig_pleth)

    time.sleep(0.5)
