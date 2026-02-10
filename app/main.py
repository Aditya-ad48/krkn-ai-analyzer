import sys
from pathlib import Path

# Add project root to Python path for module resolution
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from dotenv import load_dotenv
from src.loaders.krkn_loader import KrknResultsLoader
from src.orchestrator import Orchestrator

load_dotenv()

st.set_page_config(page_title="Krkn-AI Result Explorer", layout="wide")
st.title("🐙 Krkn-AI Result Explorer — Prototype")

st.sidebar.header("Load experiment")
upload = st.sidebar.file_uploader("Upload experiment ZIP (optional)", type=["zip"])
local_dir = st.sidebar.text_input("Or local experiment folder", "data/synthetic/experiment_1")

if upload:
    st.info("ZIP upload processing is not implemented in scaffold; please extract locally for now.")
exp_path = Path(local_dir)
if not exp_path.exists():
    st.error(f"Experiment path not found: {exp_path}")
    st.stop()

st.sidebar.success(f"Loading from {exp_path}")

loader = KrknResultsLoader(str(exp_path))
detected = loader.auto_detect_format()
st.sidebar.write(detected)

if st.sidebar.button("Load & Analyze"):
    exp = loader.load()
    orchestrator = Orchestrator()
    analysis = orchestrator.analyze_experiment(exp)
    st.session_state["exp"] = exp
    st.session_state["analysis"] = analysis
    st.success("Analysis complete — open pages in the left nav.")
else:
    st.info("Click 'Load & Analyze' to parse the experiment and run agents.")

st.markdown("""
Use the left sidebar to navigate pages:
- Dashboard
- AI Analysis
- Comparison
- Reports
""")
