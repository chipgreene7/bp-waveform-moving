import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import time

# --- Layout config ---
st.set_page_config(layout="wide")

# --- Waveform Generators ---

def generate_ecg_waveform(rhythm_type, duration=1.0, fs=500):
    t = np.linspace(0, duration, int(duration * fs))
    if rhythm_type == "Normal Sinus Rhythm":
        ecg = 0.6 * np.sin(2 * np.pi * 1.0 * t) + 0.2 * np.sin(2 * np.pi * 2.0 * t)
    elif rhythm_type == "Atrial Fibrillation":
        ecg = 0.2 * np.random.randn(len(t)) + 0.3 * np.sin(2 * np.pi * 5.5 * t)
    elif rhythm_type == "Ventricular Tachycardia":
        ecg = 0.8 * np.sign(np.sin(2 * np.pi * 3 * t))
    elif rhythm_type == "Sinus Tachycardia":
        ecg = 0.6 * np.sin(2 * np.pi * 2.0 * t) + 0.2 * np.sin(2 * np.pi * 4.0 * t)
    else:
        ecg = np.zeros_like(t)
    return t, ecg

def generate_bp_waveform(sys=120, dia=80, duration=1.0, fs=500):
    t = np.linspace(0, duration, int(duration * fs))
    waveform = (
        0.3 * np.sin(2 * np.pi * 1.0 * t) +
        0.15 * np.sin(4 * np.pi * t) +
        0.05 * np.exp(-20 * (t - 0.3)**2)
    )
    waveform = (waveform - np.min(waveform)) / (np.max(waveform) - np.min(waveform))
    waveform = waveform * (sys - dia) + dia
    return t, waveform

def generate_resp_waveform(rr=16, duration=1.0, fs=500):
    t = np.linspace(0, duration, int(duration * fs))
    waveform = 0.8 * np.sin(2 * np.pi * (rr / 60.0) * t)
    return t, waveform

# --- Presets ---
preset_cases = {
    "Normal": {"ecg": "Normal Sinus Rhythm", "sys": 120, "dia": 80, "rr": 16},
    "Sepsis": {"ecg": "Sinus Tachycardia", "sys": 90, "dia": 50, "rr": 28},
    "Hypovolemic Shock": {"ecg": "Sinus Tachycardia", "sys": 80, "dia": 40, "rr": 30},
    "AFib RVR": {"ecg": "Atrial Fibrillation", "sys": 110, "dia": 70, "rr": 22},
    "V-Tach": {"ecg": "Ventricular Tachycardia", "sys": 70, "dia": 40, "rr": 26},
    "Custom": {}  # Custom case controlled by user
}

ecg_types = ["Normal Sinus Rhythm", "Sinus Tachycardia", "Atrial Fibrillation", "Ventricular Tachycardia"]

# --- Sidebar UI ---
st.sidebar.title("🩺 VitalSim Case Selector")
selected_case = st.sidebar.selectbox("Choose a Scenario", list(preset_cases.keys()))

if selected_case == "Custom":
    st.sidebar.markdown("### Customize Vital Signs")
    sys = st.sidebar.slider("Systolic BP", 60, 200, 120)
    dia = st.sidebar.slider("Diastolic BP", 30, 120, 80)
    rr = st.sidebar.slider("Respiratory Rate (bpm)", 6, 40, 16)
    ecg_type = st.sidebar.selectbox("ECG Rhythm", ecg_types)
else:
    case = preset_cases[selected_case]
    sys = case["sys"]
    dia = case["dia"]
    rr = case["rr"]
    ecg_type = case["ecg"]

# --- Layout ---
col1, col2 = st.columns(2)
placeholder1 = col1.empty()
placeholder2 = col2.empty()
placeholder3 = st.empty()

fs = 500
duration = 2  # seconds

# --- Real-time Simulation Loop ---
for _ in range(200):
    t_ecg, ecg = generate_ecg_waveform(ecg_type, duration, fs)
    t_bp, bp = generate_bp_waveform(sys, dia, duration, fs)
    t_resp, resp = generate_resp_waveform(rr, duration, fs)

    # ECG
    fig1, ax1 = plt.subplots(figsize=(8, 2))
    ax1.plot(t_ecg, ecg, color="red")
    ax1.set_ylim(-1.5, 1.5)
    ax1.axis("off")
    ax1.set_title(f"ECG: {ecg_type}", fontsize=12)
    placeholder1.pyplot(fig1)

    # BP
    fig2, ax2 = plt.subplots(figsize=(8, 2))
    ax2.plot(t_bp, bp, color="blue")
    ax2.set_ylim(0, 200)
    ax2.axis("off")
    ax2.set_title(f"BP: {sys}/{dia} mmHg", fontsize=12)
    placeholder2.pyplot(fig2)

    # Respiratory
    fig3, ax3 = plt.subplots(figsize=(16, 1.8))
    ax3.plot(t_resp, resp, color="green")
    ax3.set_ylim(-1.5, 1.5)
    ax3.axis("off")
    ax3.set_title(f"Respiratory Rate: {rr} bpm", fontsize=12)
    placeholder3.pyplot(fig3)

    time.sleep(0.5)
