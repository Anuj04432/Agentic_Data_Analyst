"""
Interactive Streamlit UI preview for testing components/chart_selector.py.
Run with:
    streamlit run tests/test_chart_selector_ui.py
"""

import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from components.chart_selector import (
    get_available_chart_types,
    validate_chart_config,
    render_chart_selector,
)


def get_sample_dataset(dataset_type: str) -> pd.DataFrame:
    """Generate realistic test datasets for various scenarios."""
    np.random.seed(42)
    n = 50

    if dataset_type == "Standard (Mixed Types)":
        return pd.DataFrame({
            "product_id": [f"PROD-{1000 + i}" for i in range(n)],
            "category": np.random.choice(["Electronics", "Fashion", "Home & Kitchen", "Books"], size=n),
            "region": np.random.choice(["North", "South", "East", "West"], size=n),
            "units_sold": np.random.randint(10, 500, size=n),
            "unit_price": np.random.uniform(15.0, 950.0, size=n).round(2),
            "discount_pct": np.random.uniform(0.0, 0.35, size=n).round(2),
            "order_date": pd.date_range("2024-01-01", periods=n, freq="3D"),
            "is_returned": np.random.choice([True, False], size=n, p=[0.1, 0.9]),
        })

    elif dataset_type == "Categorical Only":
        return pd.DataFrame({
            "department": ["Engineering", "HR", "Sales", "Marketing", "Engineering", "Design"],
            "city": ["New York", "London", "Tokyo", "Berlin", "Paris", "Toronto"],
            "status": ["Full-time", "Contract", "Full-time", "Part-time", "Full-time", "Remote"],
        })

    elif dataset_type == "Single Numeric Column":
        return pd.DataFrame({
            "customer_id": [f"CUST-{i}" for i in range(1, 21)],
            "satisfaction_score": np.random.randint(1, 10, size=20),
        })

    elif dataset_type == "Empty DataFrame":
        return pd.DataFrame()

    return pd.DataFrame()


def render_live_plot_preview(df: pd.DataFrame, config: dict):
    """Optionally renders a live Plotly figure based on the returned config."""
    if not config.get("is_valid"):
        st.warning(f"⚠️ Configuration Incomplete: {config.get('error_message')}")
        return

    chart_type = config.get("chart_type")
    x = config.get("x")
    y = config.get("y")
    color = config.get("color")
    title = config.get("title")

    try:
        if chart_type == "Scatter Plot":
            fig = px.scatter(df, x=x, y=y, color=color, title=title)
            st.plotly_chart(fig, use_container_width=True)

        elif chart_type == "Bar Chart":
            agg = config.get("agg", "count")
            if y is None or agg == "count":
                counts = df[x].value_counts().reset_index()
                counts.columns = [x, "count"]
                fig = px.bar(counts, x=x, y="count", title=title)
            else:
                agg_df = df.groupby(x, as_index=False)[y].agg(agg)
                fig = px.bar(agg_df, x=x, y=y, title=title)
            st.plotly_chart(fig, use_container_width=True)

        elif chart_type == "Line Chart":
            fig = px.line(df, x=x, y=y, color=color, title=title)
            st.plotly_chart(fig, use_container_width=True)

        elif chart_type == "Histogram":
            bins = config.get("bins", 30)
            fig = px.histogram(df, x=x, nbins=bins, title=title)
            st.plotly_chart(fig, use_container_width=True)

        elif chart_type == "Box Plot":
            fig = px.box(df, y=y, x=x, title=title)
            st.plotly_chart(fig, use_container_width=True)

        elif chart_type == "Pie / Donut Chart":
            if y is None:
                counts = df[x].value_counts().reset_index()
                counts.columns = [x, "count"]
                fig = px.pie(counts, names=x, values="count", title=title)
            else:
                fig = px.pie(df, names=x, values=y, title=title)
            st.plotly_chart(fig, use_container_width=True)

        elif chart_type == "Correlation Heatmap":
            cols = config.get("columns", [])
            if len(cols) >= 2:
                corr = df[cols].corr()
                fig = px.imshow(corr, text_auto=True, aspect="auto", title=title, color_continuous_scale="RdBu_r")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Select at least 2 numeric features to display heatmap.")

    except Exception as exc:
        st.error(f"Error rendering chart: {exc}")


def main():
    st.set_page_config(
        page_title="Chart Selector Component Preview",
        page_icon="📊",
        layout="wide",
    )

    st.title("📊 Chart Selector Component Preview")
    st.caption("Interactive test preview for `components/chart_selector.py`.")

    # 1. Dataset Scenario Selection
    st.sidebar.header("🧪 Test Scenarios")
    dataset_option = st.sidebar.radio(
        "Choose Dataset Scenario",
        options=[
            "Standard (Mixed Types)",
            "Categorical Only",
            "Single Numeric Column",
            "Empty DataFrame",
        ],
    )

    df = get_sample_dataset(dataset_option)

    with st.expander(f"📋 Dataset Preview: {dataset_option}", expanded=False):
        if not df.empty:
            st.dataframe(df.head(10), use_container_width=True)
            st.caption(f"Shape: {df.shape[0]} rows × {df.shape[1]} columns")
        else:
            st.info("DataFrame is empty.")

    # 2. Available Chart Types Detection
    st.subheader("1. Available Chart Types (`get_available_chart_types`)")
    available_charts = get_available_chart_types(df)
    if available_charts:
        st.write("Compatible Charts:", " • ".join([f"`{c}`" for c in available_charts]))
    else:
        st.info("No compatible charts detected for this dataset structure.")

    st.divider()

    # 3. Interactive Chart Selector Component
    st.subheader("2. Interactive Widget (`render_chart_selector`)")
    config = render_chart_selector(df, key_prefix="preview")

    # 4. Returned Config Inspection
    st.divider()
    st.subheader("3. Returned Configuration Contract")

    col_cfg, col_plot = st.columns([1, 1.4])

    with col_cfg:
        st.markdown("**Structured Output Dictionary:**")
        st.json(config)

    with col_plot:
        st.markdown("**Live Rendered Plot:**")
        if not df.empty:
            render_live_plot_preview(df, config)
        else:
            st.info("No plot rendered for empty dataset.")


if __name__ == "__main__":
    main()
