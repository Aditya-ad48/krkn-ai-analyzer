import sys
from pathlib import Path

# Add project root to Python path for module resolution
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import streamlit as st
from src.loaders.krkn_loader import KrknResultsLoader
from src.visualizations.fitness_viz import fitness_evolution_chart

st.header("📈 Experiment Comparison")

base = st.text_input("Base experiment path", "data/synthetic/experiment_1")
compare = st.text_input("Comparison experiment path", "")

if st.button("Compare"):
    if not base or not compare:
        st.warning("Please provide both experiment paths.")
        st.stop()

    try:
        base_exp = KrknResultsLoader(base).load()
        cmp_exp = KrknResultsLoader(compare).load()
    except Exception as e:
        st.error(f"Failed to load experiments: {e}")
        st.stop()

    fig1 = fitness_evolution_chart(base_exp.fitness)
    fig2 = fitness_evolution_chart(cmp_exp.fitness)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Base Experiment")
        if fig1:
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.info("No fitness data in base experiment.")

    with col2:
        st.subheader("Comparison Experiment")
        if fig2:
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No fitness data in comparison experiment.")
