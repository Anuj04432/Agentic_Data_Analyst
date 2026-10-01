import sys
from pathlib import Path

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

import streamlit as st
import pandas as pd
import numpy as np
from analysis.profiling import calculate_health_score, generate_dataset_audit

# ==============================================================================
# STREAMLIT PAGE CONFIGURATION
# ==============================================================================
st.set_page_config(
    page_title="Dataset Health Score - Preview UI",
    page_icon="🩺",
    layout="wide",
)

# Custom Styling for modern cards and badges
st.markdown(
    """
    <style>
    .metric-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .metric-title {
        font-size: 13px;
        color: #64748B;
        font-weight: 600;
        text-transform: uppercase;
        margin-bottom: 4px;
    }
    .metric-value {
        font-size: 22px;
        font-weight: 700;
        color: #1E293B;
    }
    .metric-deduction {
        font-size: 13px;
        color: #EF4444;
        font-weight: 600;
        margin-top: 4px;
    }
    .summary-card {
        background-color: #F8FAFC;
        border-left: 4px solid #4F46E5;
        border-radius: 6px;
        padding: 14px 18px;
        margin-top: 15px;
        font-size: 15px;
        color: #1E293B;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🩺 Dataset Health Score & Profiling Preview")
st.caption("Interactive preview of the health scoring engine for the Agentic Data Analyst dashboard.")

# ==============================================================================
# SIDEBAR CONTROLS & TEST PRESETS
# ==============================================================================
with st.sidebar:
    st.header("⚙️ Test Scenarios")
    scenario = st.radio(
        "Choose a test dataset:",
        [
            "Default (Mixed Issues)",
            "Clean Data (Grade A)",
            "Heavy Outliers & Missing (Grade C/D)",
            "Critical Data Hygiene (Grade F)",
            "Upload Custom CSV",
        ],
    )

    st.markdown("---")
    st.markdown(
        """
        **Deduction Rules:**
        - **Missing values**: Up to -30 pts
        - **Duplicate rows**: Up to -20 pts
        - **Severe Outliers**: Up to -20 pts
        - **Constant Cols**: Up to -15 pts
        """
    )

# ==============================================================================
# DATASET GENERATION BASED ON PRESET
# ==============================================================================
if scenario == "Default (Mixed Issues)":
    data = {
        "age": [22, 25, 29, 34, 40, 28, 31, 35, 150, 24],
        "salary": [45000, 50000, 60000, 75000, 80000, 52000, 61000, 78000, 85000, 48000],
        "department": ["IT", "HR", "IT", "Finance", "HR", "IT", "Finance", "IT", "HR", "IT"],
        "city": ["New York", "London", "Paris", None, "Tokyo", "London", "Paris", "New York", None, "London"],
        "status": ["Active"] * 10,
    }
    df = pd.DataFrame(data)

elif scenario == "Clean Data (Grade A)":
    data = {
        "user_id": list(range(101, 121)),
        "age": [22, 28, 35, 41, 29, 33, 45, 52, 26, 31, 38, 44, 27, 36, 49, 30, 42, 34, 39, 48],
        "income": [45000 + i * 2500 for i in range(20)],
        "role": ["Engineer", "Designer", "Manager", "Analyst"] * 5,
    }
    df = pd.DataFrame(data)

elif scenario == "Heavy Outliers & Missing (Grade C/D)":
    vals = [10, 11, 12, 10, 11, 12, 10, 11, 100, 250]
    data = {
        "id": list(range(10)),
        "metric_a": vals,
        "metric_b": [None, 12.5, None, 14.1, 15.0, None, 18.2, None, 21.0, 22.5],
        "category": ["A", "A", "B", "B", "C", "C", "D", "D", "E", "E"],
        "constant_flag": [1] * 10,
    }
    df = pd.DataFrame(data)

elif scenario == "Critical Data Hygiene (Grade F)":
    data = {
        "col_a": [None, None, None, None, None, None],
        "col_b": [10, 10, 10, 10, 10, 10],
        "col_c": [10, 10, 10, 10, 10, 10],
        "col_d": [None, None, None, None, None, None],
    }
    df = pd.DataFrame(data)

elif scenario == "Upload Custom CSV":
    uploaded = st.file_uploader("Upload CSV file for instant profiling", type=["csv"])
    if uploaded is not None:
        df = pd.read_csv(uploaded)
    else:
        st.info("👆 Please upload a CSV file to test profiling.")
        df = pd.DataFrame()

# ==============================================================================
# CALCULATE HEALTH SCORE & RENDER UI
# ==============================================================================
if df is not None and not df.empty:
    result = calculate_health_score(df)
    score = result["health_score"]
    grade = result["grade"]
    deductions = result["deductions"]

    # Grade color mapping
    grade_colors = {
        "A": {"bg": "#10B981", "border": "#059669"},
        "B": {"bg": "#3B82F6", "border": "#2563EB"},
        "C": {"bg": "#F59E0B", "border": "#D97706"},
        "D": {"bg": "#F97316", "border": "#EA580C"},
        "F": {"bg": "#EF4444", "border": "#DC2626"},
        "N/A": {"bg": "#6B7280", "border": "#4B5563"},
    }
    color = grade_colors.get(grade, grade_colors["N/A"])

    # 1. Top Section: Hero Grade Card & Key Metrics
    col_score, col_details = st.columns([1, 3])

    with col_score:
        st.markdown(
            f"""
            <div style="background-color: {color['bg']}; border: 2px solid {color['border']}; border-radius: 12px; padding: 24px 16px; text-align: center; color: white;">
                <div style="font-size: 14px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;">Health Grade</div>
                <div style="font-size: 64px; font-weight: 800; line-height: 1.1; margin: 6px 0;">{grade}</div>
                <div style="font-size: 18px; font-weight: 600;">{score:.1f} / 100</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    audit = generate_dataset_audit(df)
    memory_formatted = audit["memory"]["formatted"]
    warnings = audit["warnings"]

    with col_details:
        st.markdown(f"### Dataset Audit: **{len(df):,} Rows** × **{len(df.columns)} Columns** ({memory_formatted})")
        st.progress(score / 100.0)

        # 4 Metric Cards for Deductions
        c1, c2, c3, c4 = st.columns(4)

        with c1:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-title">Missing Values</div>
                    <div class="metric-value">{int(df.isna().sum().sum())} cells</div>
                    <div class="metric-deduction">-{deductions['missing']:.1f} pts</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with c2:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-title">Duplicate Rows</div>
                    <div class="metric-value">{int(df.duplicated().sum())} rows</div>
                    <div class="metric-deduction">-{deductions['duplicates']:.1f} pts</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with c3:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-title">Severe Outliers</div>
                    <div class="metric-value">Col Penalty</div>
                    <div class="metric-deduction">-{deductions['outliers']:.1f} pts</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with c4:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-title">Constant Cols</div>
                    <div class="metric-value">Zero Var</div>
                    <div class="metric-deduction">-{deductions['constant_cols']:.1f} pts</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Dynamic Summary Banner
        st.markdown(
            f"""
            <div class="summary-card">
                <strong>Audit Summary:</strong> {result['summary']}
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Actionable Warnings
        if warnings and warnings != ["Dataset is empty or None."]:
            with st.expander(f"⚠️ Actionable Diagnostic Alerts ({len(warnings)})", expanded=True):
                for i,w in enumerate(warnings,1):
                    st.warning(f"{i,w}")

    st.markdown("---")

    # 2. Interactive Data Editor (Modify cells to see score change live!)
    st.subheader("📝 Live Data Table")
    st.caption("Tip: You can edit values, add rows, or delete values directly in this table to see the health score update live!")
    edited_df = st.data_editor(df, use_container_width=True, num_rows="dynamic")

    # If user modified the table, re-evaluate and notify
    if not edited_df.equals(df):
        updated_result = calculate_health_score(edited_df)
        st.info(
            f"🔄 **Live Recalculation:** New Score = **{updated_result['health_score']}/100** (Grade **{updated_result['grade']}**)"
        )

else:
    st.warning("No data available to profile.")
