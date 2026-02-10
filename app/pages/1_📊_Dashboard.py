import streamlit as st
import plotly.express as px
import pandas as pd

st.header("Experiment Overview")

if "exp" not in st.session_state:
    st.info("No experiment loaded. Go back to main and run Load & Analyze.")
    st.stop()

exp = st.session_state["exp"]
analysis = st.session_state["analysis"]

st.subheader("Metadata")
st.write(exp.metadata.model_dump())

# Fitness chart
fitness = exp.fitness
if fitness:
    df = pd.DataFrame([f.model_dump() for f in fitness])
    fig = px.line(
        df.sort_values("generation"),
        x="generation",
        y="fitness_score",
        markers=True,
        title="Fitness evolution (per scenario point)"
    )
    st.plotly_chart(fig, width="stretch")
else:
    st.warning("No fitness data available.")

# Health summary
st.subheader("Health summary")
st.json(analysis.get("health", {}))
