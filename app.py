import streamlit as st
from components.sidebar import render_sidebar
from ui.Data_Analysis import analysis_tab
from ui.Data_Visualization import visualization_tab
from utils.session_state import get_dataset, init_session_state

st.set_page_config(
    page_title="Agentic Data Analyst",
    page_icon="🤖",
    layout="wide",
)

st.title("🤖 Agentic Data Analyst")

# Initialize session state for persistent dataset and message history
init_session_state()

# Shared modular sidebar for multi-source ingestion & dataset badge
df, filename = render_sidebar()

if df is not None:
    st.caption(f"Active Dataset: **{filename}** | {df.shape[0]:,} rows × {df.shape[1]} columns")
    tab_eda, tab_viz, tab_chat = st.tabs([
        "📊 Exploratory Data Analysis",
        "📈 Data Visualization",
        "🤖 Ask Your Data",
    ])

    with tab_eda:
        analysis_tab(df)

    with tab_viz:
        visualization_tab(df)

    with tab_chat:
        st.info("🤖 Autonomous AI Data Analyst tab will be wired in Phase 6.")
else:
    st.info("👋 Welcome to **Agentic Data Analyst**! Please upload a file or select a sample dataset from the sidebar to begin.")