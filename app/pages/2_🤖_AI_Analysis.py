import streamlit as st
import plotly.graph_objects as go
from src.visualizations.heatmap import create_failure_correlation_heatmap

st.set_page_config(page_title="AI Analysis", layout="wide")
st.header("🤖 AI-Powered Root Cause Analysis")

if "analysis" not in st.session_state:
    st.warning("⚠️ Run analysis from the main page first.")
    st.stop()

# ===== ADD THIS LINE - GET EXPERIMENT DATA =====
exp = st.session_state.get("exp")  # ← CRITICAL FIX!
if not exp:
    st.error("Experiment data not found. Please load experiment from main page.")
    st.stop()

analysis = st.session_state["analysis"]

# ===== TOP-LEVEL METRICS =====
col1, col2, col3, col4 = st.columns(4)

fitness_data = analysis.get("fitness", {})
health_data = analysis.get("health", {})
slo_data = analysis.get("slo", {})
rca_data = analysis.get("root_cause", {})

with col1:
    best_fitness = fitness_data.get("best_overall", {}).get("fitness_score", 1.0)
    st.metric("Best Fitness Score", f"{best_fitness:.2f}", 
              delta=f"{(best_fitness - 1.0):.2f}", 
              delta_color="inverse")

with col2:
    failure_count = sum(health_data.get("failure_counts", {}).values())
    st.metric("Total Health Failures", failure_count)

with col3:
    slo_status = slo_data.get("status", "unknown")
    st.metric("SLO Status", slo_status.upper(), 
              delta="VIOLATED" if slo_status == "violated" else None,
              delta_color="inverse" if slo_status == "violated" else "off")

with col4:
    confidence = rca_data.get("confidence", 0.0)
    st.metric("AI Confidence", f"{confidence:.0%}")

st.divider()

# ===== ROOT CAUSE ANALYSIS =====
st.subheader("🎯 Root Cause Hypothesis")

if rca_data.get("structured"):
    # Display structured RCA
    st.markdown(f"### {rca_data.get('hypothesis', 'No hypothesis')}")
    
    # Affected Components
    components = rca_data.get("affected_components", [])
    if components:
        st.markdown("**Affected Components:**")
        cols = st.columns(min(len(components), 4))  # ← FIX: max 4 columns
        for i, comp in enumerate(components[:4]):  # ← FIX: limit to 4
            cols[i].info(f"🔴 {comp}")
    
    # Evidence Section
    st.markdown("#### 📋 Supporting Evidence")
    evidence = rca_data.get("evidence", [])
    if evidence:
        for i, ev in enumerate(evidence, 1):
            with st.expander(f"Evidence {i}: {ev.get('file', 'unknown')}"):
                st.code(f"Location: {ev.get('line', 'N/A')}", language="text")
                st.write(ev.get("detail", ""))
    else:
        st.warning("No evidence citations found")
    
    # Remediation Steps
    st.markdown("#### 🛠️ Recommended Actions")
    remediations = rca_data.get("remediations", [])
    if remediations:
        for i, rem in enumerate(remediations, 1):
            impact = rem.get("impact", "medium")
            emoji = "🔴" if impact == "high" else ("🟡" if impact == "medium" else "🟢")
            
            with st.container():
                st.markdown(f"**{i}. {rem.get('step', 'Unknown step')}** {emoji}")
                st.caption(f"**Impact:** {impact.upper()} | **Rationale:** {rem.get('rationale', '')}")
                st.divider()
    
    # Missing Data
    missing = rca_data.get("missing_data", [])
    if missing:
        st.warning("**Missing Observability Signals:**")
        for item in missing:
            st.markdown(f"- {item}")
    
    # Metadata
    if rca_data.get("metadata"):
        with st.expander("🔍 Analysis Metadata"):
            st.json(rca_data["metadata"])

else:
    # Fallback for non-structured output
    st.warning("AI analysis returned unstructured output")
    if "raw" in rca_data:
        st.markdown(rca_data["raw"])
    else:
        st.json(rca_data)

st.divider()

# ===== DETAILED AGENT OUTPUTS =====
tab1, tab2, tab3 = st.tabs(["📈 Fitness Analysis", "🏥 Health Correlation", "⚖️ SLO Validation"])

with tab1:
    st.subheader("Fitness Evolution Analysis")
    
    # Trend indicator
    trend = fitness_data.get("trend", "unknown")
    trend_emoji = "📉" if trend == "improving" else ("📈" if trend == "degrading" else "➡️")
    st.markdown(f"**Trend:** {trend_emoji} {trend.upper()}")
    
    # Per-generation table
    per_gen = fitness_data.get("per_generation", {})
    if per_gen:
        import pandas as pd
        df = pd.DataFrame([
            {
                "Generation": gen,
                "Best": data["best"],
                "Average": data["avg"],
                "Worst": data["worst"],
                "Count": data["count"]
            }
            for gen, data in sorted(per_gen.items())
        ])
        
        # Create evolution chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df["Generation"], y=df["Best"],
            mode='lines+markers', name='Best',
            line=dict(color='green', width=3)
        ))
        fig.add_trace(go.Scatter(
            x=df["Generation"], y=df["Average"],
            mode='lines+markers', name='Average',
            line=dict(color='blue', width=2, dash='dash')
        ))
        fig.add_trace(go.Scatter(
            x=df["Generation"], y=df["Worst"],
            mode='lines+markers', name='Worst',
            line=dict(color='red', width=2, dash='dot')
        ))
        
        fig.update_layout(
            title="Fitness Score Evolution Across Generations",
            xaxis_title="Generation",
            yaxis_title="Fitness Score (lower = more damaging)",
            hovermode="x unified",
            template="plotly_white"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df, use_container_width=True)

with tab2:
    st.subheader("Health Event Correlation")
    
    failure_counts = health_data.get("failure_counts", {})
    if failure_counts:
        # Failure bar chart
        import pandas as pd
        df_health = pd.DataFrame([
            {"Service": svc, "Failures": count}
            for svc, count in failure_counts.items()
        ])
        
        fig_health = go.Figure(data=[
            go.Bar(
                x=df_health["Service"],
                y=df_health["Failures"],
                marker_color='indianred'
            )
        ])
        fig_health.update_layout(
            title="Health Check Failures by Service",
            xaxis_title="Service",
            yaxis_title="Failure Count",
            template="plotly_white"
        )
        st.plotly_chart(fig_health, use_container_width=True)
    
    # MTTR
    mttr = health_data.get("mttr_seconds", {})
    if mttr:
        st.markdown("**Mean Time To Recovery (MTTR):**")
        import pandas as pd
        mttr_df = pd.DataFrame([
            {"Service": svc, "MTTR (seconds)": time}
            for svc, time in mttr.items()
        ])
        st.dataframe(mttr_df, use_container_width=True)
    
    # Cascade detection
    cascades = health_data.get("cascade_samples", [])
    if cascades:
        st.warning(f"**Cascade Failures Detected:** {len(cascades)} instances")
        with st.expander("View cascade patterns"):
            for i, cascade in enumerate(cascades, 1):
                st.markdown(f"{i}. {' → '.join(cascade)}")
    
    # ===== HEATMAP SECTION - FIXED =====
    st.markdown("#### 📊 Failure Correlation Heatmap")
    if exp.health_events:
        # ← FIXED: Define health_dicts here
        health_dicts = [
            {
                "timestamp": e.timestamp,
                "service": e.service,
                "status_code": e.status_code
            }
            for e in exp.health_events
        ]
        
        heatmap_fig = create_failure_correlation_heatmap(health_dicts)
        if heatmap_fig:
            st.plotly_chart(heatmap_fig, use_container_width=True)
            st.caption("Values close to 1.0 = services that often fail together")
        else:
            st.info("Not enough data for correlation heatmap")

with tab3:
    st.subheader("SLO Validation Results")
    
    violations = slo_data.get("violations", [])
    
    if violations:
        st.error(f"⚠️ **{len(violations)} SLO Violation(s) Detected**")
        
        for v in violations:
            v_type = v.get("type", "unknown")
            if v_type == "error_rate":
                st.markdown(f"**Error Rate:** {v['error_rate']:.1%} (threshold: {v['threshold']:.1%})")
            elif v_type == "latency_p99":
                st.markdown(f"**P99 Latency:** {v['latency_p99']}ms (threshold: {v['threshold']}ms)")
    else:
        st.success("✅ All SLOs passed")
    
    # Display metrics
    st.markdown("**Observed Metrics:**")
    col1, col2 = st.columns(2)
    with col1:
        error_rate = slo_data.get("error_rate", 0.0)
        st.metric("Error Rate", f"{error_rate:.1%}")
    with col2:
        latency = slo_data.get("latency_p99")
        if latency:
            st.metric("P99 Latency", f"{latency}ms")

st.divider()

# Export button
if st.button("📥 Export Full Analysis as JSON"):
    import json
    st.download_button(
        "Download JSON",
        data=json.dumps(analysis, indent=2),
        file_name="krkn_analysis.json",
        mime="application/json"
    )