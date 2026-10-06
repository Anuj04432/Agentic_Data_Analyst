import streamlit as st
from components.sidebar import render_sidebar
from ui.Data_Analysis import analysis_tab
from ui.Data_Visualization import visualization
from utils.session_state import get_dataset, init_session_state

st.set_page_config(page_title="Agentic Data Analyst", layout="wide")
st.title("🤖 Agentic Data Analyst")

init_session_state()

# Shared modular sidebar for multi-source ingestion & dataset badge
df, filename = render_sidebar()

if df is not None:
    st.caption(f"Active Dataset: **{filename}** | {df.shape[0]:,} rows × {df.shape[1]} columns")