import os, sys
CURRENT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, os.pardir))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import streamlit as st
from src.main import run_pipeline
from pathlib import Path
import json

st.title("Breast Cancer Diagnosis — Mini Project")
st.write("Demo: ingest → anonymise → train → report")

if st.button("Run Pipeline"):
    with st.spinner("Running pipeline..."):
        run_pipeline()
    st.success("Complete! Check the output/ folder in src/ for artifacts.")

if st.button("Show Metrics"):
    metrics_file = Path('src') / 'output' / 'metrics.json'
    if metrics_file.exists():
        st.write(json.loads(metrics_file.read_text()))
    else:
        st.write("No metrics file yet. Run the pipeline first.")
