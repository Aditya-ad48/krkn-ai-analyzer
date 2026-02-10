import streamlit as st
import json

st.header("📋 Export Report")

if "analysis" not in st.session_state or "exp" not in st.session_state:
    st.info("Run analysis first from the main page.")
    st.stop()

report = {
    "metadata": st.session_state["exp"].metadata.model_dump(),
    "analysis": st.session_state["analysis"]
}

st.download_button(
    label="Download JSON Report",
    data=json.dumps(report, indent=2),
    file_name="krkn_ai_analysis_report.json",
    mime="application/json"
)
