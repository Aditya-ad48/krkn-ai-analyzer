import sys
from pathlib import Path
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go


ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Krkn-AI Result Explorer", layout="wide")

# --- HEADER ---
st.title("🐙 Krkn-AI Experiment Result Explorer")
st.markdown("""
**Prototype Goal:** Visualize chaos experiment artifacts (JSON/CSV) to understand system resilience.
*Current Mode: Mock Data Demo*
""")

# --- 1. MOCK DATA GENERATOR (Simulating a Chaos Attack) ---
def get_mock_data():
    # Time: 60 seconds of data
    time = np.arange(0, 60, 1)
    
    # scenario: Healthy -> Attack -> Recovery
    latency = []
    fitness = []
    
    for t in time:
        base_latency = 20  # normal latency 20ms
        base_fitness = 1.0 # 100% health
        
        # CHAOS WINDOW (Seconds 20 to 40)
        if 20 <= t <= 40:
            # Latency spikes randomly between 100-500ms
            latency.append(base_latency + np.random.randint(100, 500))
            # Fitness drops because system is struggling
            fitness.append(base_fitness - (np.random.uniform(0.3, 0.6)))
        else:
            # Normal operation with slight noise
            latency.append(base_latency + np.random.randint(0, 10))
            fitness.append(base_fitness)
            
    df = pd.DataFrame({
        "Timestamp (s)": time,
        "Response Time (ms)": latency,
        "Fitness Score": fitness
    })
    return df

# --- SIDEBAR ---
st.sidebar.header("Experiment Settings")
experiment_id = st.sidebar.text_input("Experiment ID", "EXP-KRKN-001")
data_source = st.sidebar.radio("Data Source", ["Load Mock Data", "Upload CSV (Disabled)"])

if data_source == "Load Mock Data":
    df = get_mock_data()
    st.sidebar.success("Mock 'Network Partition' Data Loaded")

# --- MAIN DASHBOARD ---

# 1. TOP LEVEL METRICS
col1, col2, col3 = st.columns(3)
avg_fitness = df["Fitness Score"].mean()
max_latency = df["Response Time (ms)"].max()

with col1:
    st.metric("Overall Resilience Score", f"{avg_fitness:.2f}", delta="-0.15" if avg_fitness < 0.9 else "0")
with col2:
    st.metric("Peak Latency", f"{max_latency} ms", delta_color="inverse")
with col3:
    status = "FAILED" if avg_fitness < 0.8 else "PASSED"
    st.metric("SLO Status", status)

# 2. VISUALIZATION
st.subheader("System Behavior Analysis")

tab1, tab2 = st.tabs(["📉 Fitness & Health", "📊 Raw Data"])

with tab1:
    # Dual Axis Chart
    fig = go.Figure()

    # Trace 1: Latency (Bar/Area)
    fig.add_trace(go.Scatter(
        x=df["Timestamp (s)"], 
        y=df["Response Time (ms)"],
        name="Latency (ms)",
        fill='tozeroy',
        line=dict(color='rgba(255, 100, 100, 0.5)')
    ))

    # Trace 2: Fitness (Line)
    fig.add_trace(go.Scatter(
        x=df["Timestamp (s)"], 
        y=df["Fitness Score"],
        name="Fitness Score",
        yaxis="y2",
        line=dict(color='blue', width=3)
    ))

    # Layout for Dual Axis
    fig.update_layout(
        title="Impact of Chaos Injection on System Latency",
        xaxis_title="Experiment Duration (seconds)",
        yaxis=dict(title="Latency (ms)"),
        yaxis2=dict(title="Fitness Score", overlaying="y", side="right", range=[0, 1.2]),
        template="plotly_white",
        hovermode="x unified"
    )

    # Add annotation for the attack
    fig.add_vrect(x0=20, x1=40, fillcolor="red", opacity=0.1, 
                  annotation_text="CHAOS INJECTED", annotation_position="top left")

    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.dataframe(df)

# --- AI INSIGHT (MOCKED) ---
st.subheader("🤖 AI Analysis (Proposed Feature)")
st.info(f"""
**Analysis for {experiment_id}:** The system experienced a severe degradation between **t=20s** and **t=40s**. 
This correlates with the *Network Partition* injection. 
Although latency spiked to **{max_latency}ms**, the system self-healed after the injection stopped. 
**Recommendation:** Investigate timeout configurations to reduce latency spikes during partial outages.
""")