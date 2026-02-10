import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from src.analytics.anomaly_detection import AnomalyDetector
from src.visualizations.network_graph import ServiceDependencyGraph

st.set_page_config(page_title="Dashboard", layout="wide")
st.header("📊 Experiment Dashboard")

if "exp" not in st.session_state:
    st.warning("⚠️ Load experiment from main page first")
    st.stop()

exp = st.session_state["exp"]
analysis = st.session_state.get("analysis", {})

# ===== EXPERIMENT METADATA =====
st.subheader("Experiment Overview")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Experiment ID", exp.metadata.experiment_id)
with col2:
    st.metric("Total Scenarios", len(exp.scenarios))
with col3:
    generations = len(set(f.generation for f in exp.fitness))
    st.metric("Generations", generations)

st.divider()

# ===== FITNESS VISUALIZATION =====
st.subheader("🎯 Fitness Score Evolution")

if exp.fitness:
    df_fitness = pd.DataFrame([
        {
            "Generation": f.generation,
            "Scenario": f.scenario_id,
            "Fitness": f.fitness_score
        }
        for f in exp.fitness
    ])
    
    # Interactive scatter plot
    fig = px.scatter(
        df_fitness,
        x="Generation",
        y="Fitness",
        color="Fitness",
        hover_data=["Scenario"],
        color_continuous_scale="RdYlGn_r",  # Red = bad, Green = good
        title="Fitness Scores Across All Scenarios"
    )
    
    fig.update_layout(
        xaxis_title="Generation",
        yaxis_title="Fitness Score (lower = more effective chaos)",
        hovermode="closest",
        template="plotly_white"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Best scenarios table
    st.markdown("**Top 5 Most Effective Scenarios:**")
    top_scenarios = df_fitness.nsmallest(5, "Fitness")
    st.dataframe(top_scenarios, use_container_width=True)

st.divider()

# ===== HEALTH TIMELINE =====
st.subheader("🏥 Health Check Timeline")

if exp.health_events:
    df_health = pd.DataFrame([
        {
            "Timestamp": e.timestamp,
            "Service": e.service,
            "Status": "Healthy" if e.status_code < 400 else "Failed",
            "Status Code": e.status_code,
            "Latency (ms)": e.latency_ms or 0
        }
        for e in exp.health_events
    ])
    
    # Health status over time
    fig_timeline = px.scatter(
        df_health,
        x="Timestamp",
        y="Service",
        color="Status",
        size="Latency (ms)",
        hover_data=["Status Code"],
        color_discrete_map={"Healthy": "green", "Failed": "red"},
        title="Service Health Over Time"
    )
    
    fig_timeline.update_layout(
        xaxis_title="Time",
        yaxis_title="Service",
        template="plotly_white"
    )
    
    st.plotly_chart(fig_timeline, use_container_width=True)

st.divider()

# ===== ANOMALY DETECTION =====
st.subheader("🔍 ML-Powered Anomaly Detection")

detector = AnomalyDetector(contamination=0.15)

# ← INITIALIZE cascade_result BEFORE USE
cascade_result = {"total_cascade_events": 0, "cascades": []}

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Fitness Score Anomalies**")
    
    if exp.fitness:
        fitness_scores = [f.fitness_score for f in exp.fitness]
        generations = [f.generation for f in exp.fitness]
        
        anomaly_result = detector.detect_fitness_anomalies(fitness_scores, generations)
        
        if anomaly_result.get("anomaly_count", 0) > 0:
            st.warning(f"⚠️ {anomaly_result['anomaly_count']} anomalous scenarios detected")
            
            # Visualize anomalies
            df_fitness['is_anomaly'] = False
            for idx in anomaly_result['anomaly_indices']:
                if idx < len(df_fitness):  # ← SAFETY CHECK
                    df_fitness.loc[idx, 'is_anomaly'] = True
            
            fig_anomaly = px.scatter(
                df_fitness,
                x="Generation",
                y="Fitness",
                color="is_anomaly",
                color_discrete_map={True: "red", False: "lightblue"},
                title="Anomalous Fitness Scores Highlighted"
            )
            st.plotly_chart(fig_anomaly, use_container_width=True)
            
            # Show details
            with st.expander("View anomaly details"):
                for i, idx in enumerate(anomaly_result['anomaly_indices']):
                    if idx < len(fitness_scores):  # ← SAFETY CHECK
                        st.markdown(f"**Anomaly {i+1}:** Generation {generations[idx]}, Score: {fitness_scores[idx]:.3f}")
        else:
            st.success("✅ No significant anomalies detected")

with col2:
    st.markdown("**Cascade Failure Detection**")
    
    if exp.health_events:
        health_dicts = [
            {
                "timestamp": e.timestamp,
                "service": e.service,
                "status_code": e.status_code
            }
            for e in exp.health_events
        ]
        
        cascade_result = detector.detect_cascade_failures(health_dicts)  # ← NOW DEFINED
        
        if cascade_result['total_cascade_events'] > 0:
            st.warning(f"⚠️ {cascade_result['total_cascade_events']} cascade events detected")
            
            with st.expander("View cascade patterns"):
                for cascade in cascade_result['cascades'][:10]:  # Show top 10
                    st.markdown(f"**{cascade['timestamp']}**: {' → '.join(cascade['services'])}")
        else:
            st.success("✅ No cascade failures detected")

# Slow recovery detection
st.markdown("**Slow Recovery Detection**")
if exp.health_events:
    slow_recoveries = detector.detect_recovery_slowness(health_dicts, threshold_seconds=45.0)
    
    if slow_recoveries:
        st.error(f"🐌 {len(slow_recoveries)} slow recovery incidents")
        
        for recovery in slow_recoveries:
            severity_color = "🔴" if recovery['severity'] == "critical" else "🟡"
            st.markdown(f"{severity_color} **{recovery['service']}**: {recovery['recovery_time_seconds']:.0f}s to recover")
    else:
        st.success("✅ All services recovered quickly")

# ===== NETWORK GRAPH SECTION - FIXED =====
if exp.health_events and cascade_result['total_cascade_events'] > 0:
    st.divider()
    st.subheader("🕸️ Service Dependency Network")
    
    graph_builder = ServiceDependencyGraph()
    network_fig = graph_builder.build_graph_from_cascades(health_dicts, cascade_result['cascades'])
    
    st.plotly_chart(network_fig, use_container_width=True)
    
    st.caption("Node size = failure count | Edges = observed cascades | Color intensity = failure severity")

st.divider()

# ===== SCENARIO BREAKDOWN =====
st.subheader("🔬 Scenario Types Distribution")

if exp.scenarios:
    scenario_types = pd.DataFrame([
        {"Type": s.scenario_type, "Count": 1}
        for s in exp.scenarios
    ]).groupby("Type").sum().reset_index()
    
    fig_pie = px.pie(
        scenario_types,
        values="Count",
        names="Type",
        title="Chaos Scenario Types"
    )
    st.plotly_chart(fig_pie, use_container_width=True)

# ===== RAW DATA EXPLORER =====
with st.expander("🔍 Raw Data Explorer"):
    tab1, tab2, tab3 = st.tabs(["Scenarios", "Fitness Records", "Health Events"])
    
    with tab1:
        if exp.scenarios:
            st.dataframe([s.dict() for s in exp.scenarios], use_container_width=True)
    
    with tab2:
        if exp.fitness:
            st.dataframe([f.dict() for f in exp.fitness], use_container_width=True)
    
    with tab3:
        if exp.health_events:
            st.dataframe([h.dict() for h in exp.health_events], use_container_width=True)