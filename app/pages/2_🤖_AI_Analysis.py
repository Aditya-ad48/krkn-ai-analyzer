import streamlit as st

st.header("🤖 AI-Powered Analysis")

if "analysis" not in st.session_state:
    st.info("Run analysis from the main page first.")
    st.stop()

analysis = st.session_state["analysis"]

st.subheader("Fitness Summary")
st.json(analysis.get("fitness", {}))

st.subheader("Health Correlation")
st.json(analysis.get("health", {}))

st.subheader("SLO Validation")
st.json(analysis.get("slo", {}))

st.subheader("Root Cause Hypothesis")
rc = analysis.get("root_cause", {})
if isinstance(rc, dict):
    if "raw" in rc:
        # Render the LLM response as markdown
        st.markdown(rc["raw"])
        
        # Show metadata if available
        if rc.get("model"):
            st.caption(f"Model: {rc['model']} | Tokens: {rc.get('tokens_used', 'N/A')}")
    else:
        st.json(rc)
else:
    st.write(rc)
