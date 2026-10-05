"""
Interactive Streamlit UI preview for testing components/column_selector.py.
Run with:
    streamlit run tests/test_column_selector_ui.py
"""

import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np
import pandas as pd
import streamlit as st

from components.column_selector import (
    classify_columns,
    filter_columns_by_type,
    render_column_select,
    render_column_multiselect,
    render_type_aware_selector,
)


def get_sample_dataset() -> pd.DataFrame:
    """Generate a rich sample DataFrame with all data types."""
    np.random.seed(42)
    n = 20
    return pd.DataFrame({
        "employee_id": [f"EMP-{100 + i}" for i in range(n)],
        "name": [f"Person {chr(65 + i % 26)}" for i in range(n)],
        "age": np.random.randint(22, 65, size=n),
        "salary": np.random.uniform(40000, 150000, size=n).round(2),
        "performance_score": np.random.uniform(1.0, 5.0, size=n).round(2),
        "department": np.random.choice(["Engineering", "Sales", "HR", "Marketing"], size=n),
        "hire_date": pd.date_range("2021-01-01", periods=n, freq="ME"),
        "is_active": np.random.choice([True, False], size=n, p=[0.8, 0.2]),
    })


def main():
    st.set_page_config(page_title="Column Selector Component Preview", layout="wide")
    st.title("🎯 Smart Column Selector Component Preview")
    st.caption("Interactive preview for validating `components/column_selector.py`.")

    df = get_sample_dataset()

    with st.expander("👀 View Sample DataFrame", expanded=False):
        st.dataframe(df, use_container_width=True)

    # 1. Classification Overview
    st.subheader("1. Data Type Classification (`classify_columns`)")
    classified = classify_columns(df)
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("All Columns", len(classified["all"]))
    c2.metric("Numeric", len(classified["numeric"]))
    c3.metric("Categorical", len(classified["categorical"]))
    c4.metric("Datetime", len(classified["datetime"]))
    c5.metric("Boolean", len(classified["boolean"]))

    st.divider()

    # 2. Single Select
    st.subheader("2. Single-Select Dropdowns (`render_column_select`)")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Numeric Target Feature (Excluding `age`)**")
        target_col = render_column_select(
            df=df,
            label="Select Target Column",
            column_type="numeric",
            exclude_columns=["age"],
            key="demo_single_target",
            help_text="Select a numeric target variable for regression",
        )
        st.info(f"Selected Target: **{target_col}**")

    with col2:
        st.markdown("**Optional Categorical Grouping (Allow None)**")
        group_col = render_column_select(
            df=df,
            label="Select Grouping Column",
            column_type="categorical",
            allow_none=True,
            none_label="-- No Grouping (Overall) --",
            key="demo_single_group",
            help_text="Optionally segment distributions by group",
        )
        st.info(f"Selected Grouping: **{group_col}**")

    st.divider()

    # 3. Multiselect
    st.subheader("3. Multi-Select Dropdowns (`render_column_multiselect`)")
    m_col1, m_col2 = st.columns(2)

    with m_col1:
        st.markdown("**Numeric Features for Correlation Heatmap (`default_all=True`)**")
        corr_cols = render_column_multiselect(
            df=df,
            label="Select Features for Matrix",
            column_type="numeric",
            default_all=True,
            key="demo_multi_corr",
        )
        st.info(f"Selected for correlation ({len(corr_cols)}): **{corr_cols}**")

    with m_col2:
        st.markdown("**Columns to Exclude / Drop (`max_selections=2`)**")
        drop_cols = render_column_multiselect(
            df=df,
            label="Select Columns to Drop",
            column_type="all",
            default_columns=["employee_id"],
            max_selections=2,
            key="demo_multi_drop",
        )
        st.info(f"Selected to drop: **{drop_cols}**")

    st.divider()

    # 4. Type-Aware Switcher Selector
    st.subheader("4. Type-Aware Dynamic Selector (`render_type_aware_selector`)")
    s_col1, s_col2 = st.columns(2)

    with s_col1:
        st.markdown("**Single Column with Live Type Category Switcher**")
        chosen_col = render_type_aware_selector(
            df=df,
            label="Select Feature",
            key_prefix="demo_type_aware_single",
            allow_none=True,
        )
        st.success(f"Chosen Feature: **{chosen_col}**")

    with s_col2:
        st.markdown("**Multi-Column with Live Type Category Switcher**")
        chosen_multi = render_type_aware_selector(
            df=df,
            label="Select Features Subset",
            key_prefix="demo_type_aware_multi",
            multiselect=True,
            default_all=True,
        )
        st.success(f"Chosen Subset ({len(chosen_multi)}): **{chosen_multi}**")


if __name__ == "__main__":
    main()
