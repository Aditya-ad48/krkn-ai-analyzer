import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from pathlib import Path
from src.loaders.krkn_loader import KrknResultsLoader
from src.orchestrator import Orchestrator

st.set_page_config(page_title="Comparison", layout="wide")
st.header("📈 Multi-Experiment Comparison")

# Allow loading second experiment
st.sidebar.header("Load Second Experiment")
exp2_path = st.sidebar.text_input("Experiment 2 path", "data/synthetic/experiment_2")

if st.sidebar.button("Load Experiment 2"):
    if Path(exp2_path).exists():
        loader2 = KrknResultsLoader(exp2_path)
        exp2 = loader2.load()
        orchestrator = Orchestrator()
        analysis2 = orchestrator.analyze_experiment(exp2)
        
        st.session_state["exp2"] = exp2
        st.session_state["analysis2"] = analysis2
        st.success(f"Loaded {exp2.metadata.experiment_id}")
    else:
        st.error(f"Path not found: {exp2_path}")

# Check if both experiments loaded
if "exp" not in st.session_state:
    st.warning("Load Experiment 1 from main page first")
    st.stop()

exp1 = st.session_state["exp"]
analysis1 = st.session_state.get("analysis", {})

if "exp2" not in st.session_state:
    st.info("👈 Load a second experiment from the sidebar to compare")
    st.stop()

exp2 = st.session_state["exp2"]
analysis2 = st.session_state["analysis2"]

# ===== SIDE-BY-SIDE METRICS =====
st.subheader("⚖️ Head-to-Head Comparison")

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"### 🔵 {exp1.metadata.experiment_id}")
    fitness1 = analysis1.get("fitness", {})
    best1 = fitness1.get("best_overall", {}).get("fitness_score", 1.0)
    st.metric("Best Fitness", f"{best1:.3f}")
    
    health1 = analysis1.get("health", {})
    failures1 = sum(health1.get("failure_counts", {}).values())
    st.metric("Total Failures", failures1)
    
    slo1 = analysis1.get("slo", {})
    st.metric("SLO Status", slo1.get("status", "unknown").upper())

with col2:
    st.markdown(f"### 🟢 {exp2.metadata.experiment_id}")
    fitness2 = analysis2.get("fitness", {})
    best2 = fitness2.get("best_overall", {}).get("fitness_score", 1.0)
    delta = best2 - best1
    st.metric("Best Fitness", f"{best2:.3f}", delta=f"{delta:+.3f}", delta_color="inverse")
    
    health2 = analysis2.get("health", {})
    failures2 = sum(health2.get("failure_counts", {}).values())
    delta_f = failures2 - failures1
    st.metric("Total Failures", failures2, delta=f"{delta_f:+d}", delta_color="inverse")
    
    slo2 = analysis2.get("slo", {})
    st.metric("SLO Status", slo2.get("status", "unknown").upper())

st.divider()

# ===== FITNESS EVOLUTION COMPARISON =====
st.subheader("📊 Fitness Evolution Comparison")

df1 = pd.DataFrame([
    {"Generation": f.generation, "Fitness": f.fitness_score, "Experiment": exp1.metadata.experiment_id}
    for f in exp1.fitness
])

df2 = pd.DataFrame([
    {"Generation": f.generation, "Fitness": f.fitness_score, "Experiment": exp2.metadata.experiment_id}
    for f in exp2.fitness
])

df_combined = pd.concat([df1, df2])

# Group by generation and experiment
df_agg = df_combined.groupby(["Generation", "Experiment"])["Fitness"].mean().reset_index()

fig = go.Figure()

for exp_name in df_agg["Experiment"].unique():
    exp_data = df_agg[df_agg["Experiment"] == exp_name]
    fig.add_trace(go.Scatter(
        x=exp_data["Generation"],
        y=exp_data["Fitness"],
        mode='lines+markers',
        name=exp_name,
        line=dict(width=3)
    ))

fig.update_layout(
    title="Average Fitness Score Evolution",
    xaxis_title="Generation",
    yaxis_title="Fitness Score",
    hovermode="x unified",
    template="plotly_white"
)

st.plotly_chart(fig, use_container_width=True)

st.divider()

# ===== WINNER ANALYSIS =====
st.subheader("🏆 Winner Analysis")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**Best Overall Fitness**")
    winner = exp1.metadata.experiment_id if best1 < best2 else exp2.metadata.experiment_id
    st.success(f"🏆 {winner}")
    st.caption(f"{best1:.3f} vs {best2:.3f}")

with col2:
    st.markdown("**Fewer Failures**")
    winner = exp1.metadata.experiment_id if failures1 < failures2 else exp2.metadata.experiment_id
    st.success(f"🏆 {winner}")
    st.caption(f"{failures1} vs {failures2}")

with col3:
    st.markdown("**Faster Convergence**")
    gens1 = len(fitness1.get("per_generation", {}))
    gens2 = len(fitness2.get("per_generation", {}))
    winner = exp1.metadata.experiment_id if gens1 < gens2 else exp2.metadata.experiment_id
    st.success(f"🏆 {winner}")
    st.caption(f"{gens1} vs {gens2} generations")

st.divider()

# ===== DETAILED COMPARISON TABLE =====
st.subheader("📋 Detailed Metrics Comparison")

comparison_data = {
    "Metric": [
        "Best Fitness Score",
        "Average Fitness Score",
        "Total Scenarios Tested",
        "Generations",
        "Health Failures",
        "SLO Violations",
        "MTTR (avg seconds)"
    ],
    exp1.metadata.experiment_id: [
        f"{best1:.3f}",
        f"{fitness1.get('per_generation', {}).get(0, {}).get('avg', 0):.3f}",
        len(exp1.scenarios),
        len(fitness1.get("per_generation", {})),
        failures1,
        len(slo1.get("violations", [])),
        f"{sum(health1.get('mttr_seconds', {}).values()) / max(len(health1.get('mttr_seconds', {})), 1):.1f}"
    ],
    exp2.metadata.experiment_id: [
        f"{best2:.3f}",
        f"{fitness2.get('per_generation', {}).get(0, {}).get('avg', 0):.3f}",
        len(exp2.scenarios),
        len(fitness2.get("per_generation", {})),
        failures2,
        len(slo2.get("violations", [])),
        f"{sum(health2.get('mttr_seconds', {}).values()) / max(len(health2.get('mttr_seconds', {})), 1):.1f}"
    ]
}

st.table(pd.DataFrame(comparison_data))