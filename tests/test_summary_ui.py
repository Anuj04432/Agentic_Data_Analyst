"""
Interactive Streamlit Test UI for components/dataset_summary.py.
Run with: streamlit run test_summary_ui.py
"""

import sys
from pathlib import Path

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

import streamlit as st
import pandas as pd
import numpy as np

from components.dataset_summary import render_dataset_summary, extract_summary_metrics
from analysis.profiling import generate_dataset_audit


# ==============================================================================
# PAGE CONFIGURATION
# ==============================================================================
st.set_page_config(
    page_title="Dataset Summary Component - Interactive Test Bench",
    page_icon="📊",
    layout="wide",
)

st.title("📊 Dataset Summary Component - Interactive Test Bench")
st.caption("Visual test harness for verifying the 5-column KPI metrics component across multiple scenarios.")

# ==============================================================================
# SIDEBAR CONTROLS & TEST SCENARIOS
# ==============================================================================
with st.sidebar:
    st.header("⚙️ Test Scenarios")
    scenario = st.radio(
        "Select a dataset scenario:",
        [
            "Clean Data (0 missing, 0 dupes)",
            "Messy Data (Missing values & Duplicates)",
            "Empty Dataset (Edge Case)",
            "Single Column & Row (Minimal)",
            "Upload Custom File (CSV/Excel)",
        ],
    )

    st.markdown("---")
    st.header("🎨 Component Options")
    use_border = st.checkbox("Card Border (container)", value=True)
    input_mode = st.radio(
        "Input Mode passed to component:",
        ["Direct DataFrame (df=df)", "Pre-computed Audit (audit=audit)"],
    )

# ==============================================================================
# DATASET GENERATOR
# ==============================================================================
df = None

if scenario == "Clean Data (0 missing, 0 dupes)":
    df = pd.DataFrame({
        "employee_id": [101, 102, 103, 104, 105, 106, 107, 108],
        "department": ["Sales", "Engineering", "Marketing", "HR", "Sales", "Engineering", "Legal", "Finance"],
        "salary": [65000, 115000, 72000, 58000, 69000, 128000, 95000, 88000],
        "tenure_years": [2.5, 4.0, 1.5, 3.0, 2.0, 6.5, 5.0, 3.5],
        "active": [True, True, True, True, True, True, True, True],
    })

elif scenario == "Messy Data (Missing values & Duplicates)":
    df = pd.DataFrame({
        "id": [1, 2, 3, 3, 4, 5, 5, 6, 7, 8],
        "customer": ["Alice", "Bob", "Charlie", "Charlie", "David", None, None, "Frank", "Grace", None],
        "order_amount": [250.0, None, 180.5, 180.5, 420.0, 50.0, 50.0, None, 310.0, 95.0],
        "rating": [5, 4, 3, 3, None, 2, 2, 4, None, 1],
    })

elif scenario == "Empty Dataset (Edge Case)":
    df = pd.DataFrame()

elif scenario == "Single Column & Row (Minimal)":
    df = pd.DataFrame({"single_val": [42]})

elif scenario == "Upload Custom File (CSV/Excel)":
    uploaded = st.sidebar.file_uploader("Upload CSV or Excel file", type=["csv", "xlsx", "xls"])
    if uploaded is not None:
        try:
            if uploaded.name.endswith(".csv"):
                df = pd.read_csv(uploaded)
            else:
                df = pd.read_excel(uploaded)
            st.sidebar.success(f"Loaded: {uploaded.name} ({len(df):,} rows)")
        except Exception as e:
            st.sidebar.error(f"Error loading file: {e}")
            df = None
    else:
        st.info("👆 Please upload a CSV or Excel file in the sidebar to test.")
        df = None

# ==============================================================================
# COMPONENT RENDERING
# ==============================================================================
st.markdown("### 1. Live Rendered Component")

if df is not None:
    if input_mode == "Pre-computed Audit (audit=audit)" and not df.empty:
        with st.spinner("Generating audit dictionary..."):
            audit = generate_dataset_audit(df)
        metrics = render_dataset_summary(audit=audit, border=use_border)
    else:
        metrics = render_dataset_summary(df=df, border=use_border)
else:
    metrics = render_dataset_summary(df=None, border=use_border)

st.markdown("---")

# ==============================================================================
# LIVE INTERACTIVE DATA TABLE
# ==============================================================================
st.markdown("### 2. Live Data Editor")
st.caption("💡 **Tip:** Edit values, delete cells to add NaNs, or add duplicate rows directly in this table to see the KPI cards above react live!")

if df is not None and not df.empty:
    edited_df = st.data_editor(df, use_container_width=True, num_rows="dynamic")

    if not edited_df.equals(df):
        st.info("🔄 Table edited! Refreshing metric calculation with edited data...")
        fresh_metrics = extract_summary_metrics(df=edited_df)
        st.json(fresh_metrics)
else:
    st.write("No active table data to display.")

# ==============================================================================
# RAW METRICS DEBUG INSPECTOR
# ==============================================================================
with st.expander("🔍 Inspect Raw Extracted Metrics Dictionary"):
    st.json(metrics)
