"""
Interactive Streamlit UI preview for testing components/data_preview.py.
Run with:
    streamlit run tests/test_data_preview_ui.py
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

from components.dataset_summary import render_dataset_summary
from components.data_preview import render_data_preview
from utils.file_handler import dataset_format


def get_mock_datasets() -> dict[str, pd.DataFrame]:
    """Generates synthetic test datasets for UI testing."""
    # 1. Mixed types dataset
    np.random.seed(42)
    n = 150
    cities = ["New York", "London", "Tokyo", "Berlin", "Paris", "Sydney", "Toronto"]
    depts = ["Engineering", "Marketing", "Sales", "Design", "HR", "Finance"]

    df_mixed = pd.DataFrame({
        "Employee ID": [f"EMP-{1000 + i}" for i in range(n)],
        "Full Name": [f"Person {i + 1}" for i in range(n)],
        "Department": np.random.choice(depts, size=n),
        "Location": np.random.choice(cities, size=n),
        "Salary ($)": np.random.randint(45000, 160000, size=n),
        "Rating (1-5)": np.round(np.random.uniform(2.5, 5.0, size=n), 1),
        "Is Remote": np.random.choice([True, False], size=n, p=[0.4, 0.6]),
        "Hire Date": pd.date_range("2020-01-01", periods=n, freq="W").strftime("%Y-%m-%d"),
    })
    # Add a few intentional NaNs to test rendering
    df_mixed.loc[np.random.choice(n, size=5, replace=False), "Salary ($)"] = np.nan
    df_mixed.loc[np.random.choice(n, size=3, replace=False), "Department"] = np.nan

    # 2. Small edge-case dataset
    df_edge = pd.DataFrame({
        "item": ["Apple", "Banana", "Orange", "$ Special Item *", "Item (Beta)"],
        "price": [1.2, 0.5, 0.8, 99.99, 15.0],
        "in_stock": [True, True, False, True, False],
    })

    return {
        "Mock: Employees & Salaries (150 rows)": df_mixed,
        "Mock: Edge Cases & Special Characters (5 rows)": df_edge,
    }


def main():
    st.set_page_config(
        page_title="Data Preview Component - Test UI",
        page_icon="🔍",
        layout="wide",
    )

    st.title("🔍 Data Preview Component - Interactive Test UI")
    st.caption("Live sandbox to test and verify `components/data_preview.py`.")

    # Sidebar: Dataset selection & source
    with st.sidebar:
        st.header("⚙️ Data Source")

        source_type = st.radio(
            "Select dataset source:",
            ["Sample Datasets", "Synthetic Mock Data", "Upload File"],
        )

        df = None

        if source_type == "Sample Datasets":
            sample_dir = PROJECT_ROOT / "data" / "sample"
            sample_files = list(sample_dir.glob("*.*")) if sample_dir.exists() else []

            if sample_files:
                selected_sample = st.selectbox(
                    "Choose sample file:",
                    options=sample_files,
                    format_func=lambda p: p.name,
                )
                try:
                    df = dataset_format(selected_sample, selected_sample.name)
                except Exception as e:
                    st.error(f"Error loading file: {e}")
            else:
                st.warning("No sample files found in `data/sample/`.")

        elif source_type == "Synthetic Mock Data":
            mocks = get_mock_datasets()
            selected_mock = st.selectbox("Choose mock dataset:", list(mocks.keys()))
            df = mocks[selected_mock]

        elif source_type == "Upload File":
            uploaded_file = st.file_uploader(
                "Upload a CSV or Excel file",
                type=["csv", "xlsx", "xls", "json"],
            )
            if uploaded_file:
                try:
                    df = dataset_format(uploaded_file, uploaded_file.name)
                except Exception as e:
                    st.error(f"Error parsing upload: {e}")

        st.markdown("---")
        default_page_size = st.selectbox(
            "Initial default rows per page:",
            [10, 25, 50, 100],
            index=1,
        )

    if df is None or df.empty:
        st.info("👈 Please select or upload a dataset in the sidebar to start testing.")
        return

    # Section 1: KPI Summary Card Preview
    st.subheader("1. Dataset Summary KPI Cards")
    render_dataset_summary(df, border=True)

    st.markdown("---")

    # Section 2: Interactive Data Preview
    st.subheader("2. Interactive Data Preview Component")
    st.markdown(
        """
        **Test Checklist:**
        * Type in **Search rows** (try keywords, numbers, special characters like `$`, `*`).
        * Deselect columns in **Columns to display** to test projection.
        * Change **Rows per page** (`10`, `25`, `50`, `All`).
        * Test **Previous / Next** pagination buttons.
        * Click **Download View (CSV)** to verify export.
        """
    )

    # Render component under test
    displayed_slice = render_data_preview(
        df=df,
        default_page_size=default_page_size,
        key_prefix="test_preview_ui",
    )

    # Section 3: Diagnostic Inspector
    with st.expander("🔬 Component Output Inspector (Debug Info)", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Displayed Rows", len(displayed_slice))
        with col2:
            st.metric("Displayed Columns", len(displayed_slice.columns))
        with col3:
            st.metric("Memory of Slice", f"{displayed_slice.memory_usage().sum():,} B")

        st.write("Column Data Types in Current View:")
        st.json({col: str(dtype) for col, dtype in displayed_slice.dtypes.items()})


if __name__ == "__main__":
    main()
