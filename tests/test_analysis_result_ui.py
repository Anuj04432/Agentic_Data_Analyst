"""
Interactive Streamlit UI preview for testing components/analysis_result.py.
Run with:
    streamlit run tests/test_analysis_result_ui.py
"""

import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import streamlit as st

from components.analysis_result import (
    render_health_grade_badge,
    render_health_score_card,
    render_actionable_warnings,
    render_distribution_badge,
    render_correlation_badge,
)
from analysis.profiling import calculate_health_score, generate_dataset_audit


def main():
    st.set_page_config(page_title="Analysis Result Components Preview", layout="wide")
    st.title("🎨 Analysis Result Components Preview")
    st.caption("Visual inspection for badges, health cards, and diagnostic alerts.")

    # 1. Health Grade Badges
    st.subheader("1. Health Grade Badges (`render_health_grade_badge`)")
    b_col1, b_col2, b_col3, b_col4, b_col5 = st.columns(5)
    with b_col1:
        render_health_grade_badge("A", score=95.2, size="medium")
    with b_col2:
        render_health_grade_badge("B", score=84.0, size="medium")
    with b_col3:
        render_health_grade_badge("C", score=73.5, size="medium")
    with b_col4:
        render_health_grade_badge("D", score=62.1, size="medium")
    with b_col5:
        render_health_grade_badge("F", score=41.0, size="medium")

    st.divider()

    # 2. Distribution Badges
    st.subheader("2. Distribution Badges (`render_distribution_badge`)")
    d_col1, d_col2, d_col3, d_col4, d_col5 = st.columns(5)
    with d_col1:
        render_distribution_badge("Fairly Symmetrical")
    with d_col2:
        render_distribution_badge("Moderately Skewed (Right)")
    with d_col3:
        render_distribution_badge("Highly Skewed (Right)")
    with d_col4:
        render_distribution_badge("Moderately Skewed (Left)")
    with d_col5:
        render_distribution_badge("Highly Skewed (Left)")

    st.divider()

    # 3. Correlation Badges
    st.subheader("3. Correlation Badges (`render_correlation_badge`)")
    c_col1, c_col2, c_col3, c_col4, c_col5 = st.columns(5)
    with c_col1:
        render_correlation_badge(0.92)
    with c_col2:
        render_correlation_badge(0.54)
    with c_col3:
        render_correlation_badge(-0.08)
    with c_col4:
        render_correlation_badge(-0.48)
    with c_col5:
        render_correlation_badge(-0.89)

    st.divider()

    # 4. Health Score Hero Cards
    st.subheader("4. Health Score Hero Cards (`render_health_score_card`)")

    # Sample mock health data
    sample_df = pd.DataFrame({
        "id": [1, 2, 3, 4, 5, 5],
        "feature_a": [10.0, 12.0, np.nan, 14.0, 100.0, 100.0],
        "feature_b": ["x", "x", "x", "x", "x", "x"],
    })
    audit = generate_dataset_audit(sample_df)

    st.markdown("#### Sample Dataset Health Card")
    render_health_score_card(audit["health"])

    st.divider()

    # 5. Actionable Diagnostic Alerts
    st.subheader("5. Actionable Diagnostic Alerts (`render_actionable_warnings`)")
    render_actionable_warnings(audit["warnings"], expanded=True)

    st.markdown("#### Clean Dataset Example")
    render_actionable_warnings([], expanded=True)


if __name__ == "__main__":
    import numpy as np
    main()
