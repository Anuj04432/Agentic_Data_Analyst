import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as ex
import streamlit as st
from typing import Any,Dict,List,Optional,Tuple

from components.column_selector import classify_columns

def get_available_chart_types(df: Optional[pd.DataFrame]) -> List[str]:
    """
    Returns a list of viable chart types based on available column data types.

    Args:
        df: Input pandas DataFrame to evaluate.

    Returns:
        List of chart names that can be sensibly rendered for this dataset.
    """
    if df is None or df.empty:
        return []

    col_types = classify_columns(df)
    num_cols = col_types.get("numeric", [])
    cat_cols = col_types.get("categorical", [])
    date_cols = col_types.get("datetime", [])
    bool_cols = col_types.get("boolean", [])

    has_numeric = len(num_cols) > 0
    has_two_numeric = len(num_cols) >= 2
    has_categorical = len(cat_cols) > 0 or len(bool_cols) > 0
    has_datetime = len(date_cols) > 0

    available_charts: List[str] = []

    # 1. Bar Chart: suitable for categorical breakdown or numeric aggregation
    if has_categorical or has_numeric:
        available_charts.append("Bar Chart")

    # 2. Line Chart: best for time-series or sequential trends
    if has_numeric and (has_datetime or len(df) > 1):
        available_charts.append("Line Chart")

    # 3. Scatter Plot: requires at least 2 numeric features (X and Y)
    if has_two_numeric:
        available_charts.append("Scatter Plot")

    # 4. Histogram: requires at least 1 numeric feature for distributions
    if has_numeric:
        available_charts.append("Histogram")

    # 5. Box Plot: requires at least 1 numeric feature for spread & outliers
    if has_numeric:
        available_charts.append("Box Plot")

    # 6. Pie / Donut Chart: best for categorical share / proportions
    if has_categorical:
        available_charts.append("Pie / Donut Chart")

    # 7. Correlation Heatmap: requires at least 2 numeric features
    if has_two_numeric:
        available_charts.append("Correlation Heatmap")

    return available_charts


def validate_chart_config(config: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Validates whether the chosen chart configuration has all required dimensions.

    Args:
        config: Dictionary containing chart configuration keys:
            - "chart_type": str
            - "x": Optional[str]
            - "y": Optional[str]
            - "columns": Optional[List[str]] (for heatmaps)
            - "bins": Optional[int] (for histograms)

    Returns:
        Tuple of (is_valid: bool, error_message: Optional[str]).
    """
    if not isinstance(config, dict) or not config:
        return False, "Chart configuration dictionary is empty or invalid."

    chart_type = config.get("chart_type")
    if not chart_type:
        return False, "Chart type must be specified."

    x = config.get("x")
    y = config.get("y")

    if chart_type in ("Scatter Plot", "Line Chart"):
        if not x:
            return False, f"{chart_type} requires an X-axis column."
        if not y:
            return False, f"{chart_type} requires a Y-axis column."

    elif chart_type in ("Bar Chart", "Histogram", "Pie / Donut Chart"):
        if not x:
            label = "a category" if chart_type != "Histogram" else "a numeric"
            return False, f"{chart_type} requires {label} column for the X-axis."

    elif chart_type == "Box Plot":
        if not y and not x:
            return False, "Box Plot requires at least one numeric column."

    elif chart_type == "Correlation Heatmap":
        columns = config.get("columns", [])
        if not columns or len(columns) < 2:
            return False, "Correlation Heatmap requires at least 2 numeric columns."

    # Validate bins if specified for histogram
    if chart_type == "Histogram" and "bins" in config:
        bins = config.get("bins")
        if bins is not None and (not isinstance(bins, int) or bins <= 0):
            return False, "Histogram bins must be a positive integer."

    return True, None


def render_chart_selector(
    df: Optional[pd.DataFrame],
    key_prefix: str = "chart",
) -> Dict[str, Any]:
    """
    Renders an interactive Streamlit widget for selecting and configuring charts.

    Args:
        df: Input pandas DataFrame to visualize.
        key_prefix: Unique key prefix for Streamlit widgets to avoid key collisions.

    Returns:
        Standardized ChartConfig dictionary containing:
            - "chart_type": Selected chart type name
            - "x": Primary X column name
            - "y": Primary Y column name (or None)
            - "color": Hue/Grouping column name (or None)
            - "agg": Aggregation function (or None)
            - "bins": Number of histogram bins (or None)
            - "columns": List of feature columns (for Heatmaps)
            - "title": Chart title
            - "is_valid": Boolean flag indicating if configuration is valid
            - "error_message": Detailed validation error if invalid, else None
    """
    empty_result: Dict[str, Any] = {
        "chart_type": None,
        "x": None,
        "y": None,
        "color": None,
        "agg": None,
        "bins": None,
        "columns": [],
        "title": "",
        "is_valid": False,
        "error_message": "Dataset is empty or not loaded.",
    }

    if df is None or df.empty:
        st.info("ℹ️ Please load a dataset to configure visualizations.")
        return empty_result

    available_charts = get_available_chart_types(df)
    if not available_charts:
        st.warning("⚠️ No compatible chart types available for this dataset structure.")
        empty_result["error_message"] = "No compatible chart types available."
        return empty_result

    col_types = classify_columns(df)
    num_cols = col_types.get("numeric", [])
    cat_cols = col_types.get("categorical", [])
    date_cols = col_types.get("datetime", [])
    bool_cols = col_types.get("boolean", [])
    discrete_cols = cat_cols + bool_cols if (cat_cols or bool_cols) else list(df.columns)
    all_cols = list(df.columns)

    # 1. Chart Type Selection
    selected_chart = st.selectbox(
        "Select Chart Type",
        options=available_charts,
        key=f"{key_prefix}_chart_type",
    )

    x: Optional[str] = None
    y: Optional[str] = None
    color: Optional[str] = None
    agg: Optional[str] = None
    bins: Optional[int] = None
    columns: List[str] = []

    # 2. Dynamic Form Layout based on selected chart type
    if selected_chart == "Scatter Plot":
        col1, col2, col3 = st.columns(3)
        with col1:
            x = st.selectbox("X-Axis (Numeric)", options=num_cols, key=f"{key_prefix}_scatter_x")
        with col2:
            default_y_idx = 1 if len(num_cols) > 1 else 0
            y = st.selectbox("Y-Axis (Numeric)", options=num_cols, index=default_y_idx, key=f"{key_prefix}_scatter_y")
        with col3:
            color_options = [None] + discrete_cols + num_cols
            color = st.selectbox("Color / Hue (Optional)", options=color_options, key=f"{key_prefix}_scatter_color")

    elif selected_chart == "Line Chart":
        col1, col2, col3 = st.columns(3)
        with col1:
            x_options = date_cols + num_cols if (date_cols or num_cols) else all_cols
            x = st.selectbox("X-Axis (Date / Sequence)", options=x_options, key=f"{key_prefix}_line_x")
        with col2:
            y = st.selectbox("Y-Axis (Numeric)", options=num_cols, key=f"{key_prefix}_line_y")
        with col3:
            color = st.selectbox("Group by / Color (Optional)", options=[None] + discrete_cols, key=f"{key_prefix}_line_color")

    elif selected_chart == "Bar Chart":
        col1, col2, col3 = st.columns(3)
        with col1:
            x_options = discrete_cols if discrete_cols else all_cols
            x = st.selectbox("Category (X-Axis)", options=x_options, key=f"{key_prefix}_bar_x")
        with col2:
            y_options = ["None (Count Rows)"] + num_cols
            selected_y = st.selectbox("Metric (Y-Axis)", options=y_options, key=f"{key_prefix}_bar_y")
            y = None if selected_y == "None (Count Rows)" else selected_y
        with col3:
            if y is not None:
                agg = st.selectbox("Aggregation", options=["mean", "sum", "median", "count"], key=f"{key_prefix}_bar_agg")
            else:
                agg = "count"

    elif selected_chart == "Histogram":
        col1, col2 = st.columns(2)
        with col1:
            x = st.selectbox("Numeric Column", options=num_cols, key=f"{key_prefix}_hist_x")
        with col2:
            bins = st.slider("Number of Bins", min_value=5, max_value=100, value=30, step=5, key=f"{key_prefix}_hist_bins")

    elif selected_chart == "Box Plot":
        col1, col2 = st.columns(2)
        with col1:
            y = st.selectbox("Value Column (Numeric)", options=num_cols, key=f"{key_prefix}_box_y")
        with col2:
            x = st.selectbox("Group by (Category, Optional)", options=[None] + discrete_cols, key=f"{key_prefix}_box_x")

    elif selected_chart == "Pie / Donut Chart":
        col1, col2 = st.columns(2)
        with col1:
            x = st.selectbox("Category Column", options=discrete_cols, key=f"{key_prefix}_pie_x")
        with col2:
            y_options = ["None (Count Rows)"] + num_cols
            selected_y = st.selectbox("Value Column (Optional)", options=y_options, key=f"{key_prefix}_pie_y")
            y = None if selected_y == "None (Count Rows)" else selected_y

    elif selected_chart == "Correlation Heatmap":
        columns = st.multiselect(
            "Select Numeric Features",
            options=num_cols,
            default=num_cols[: min(8, len(num_cols))],
            key=f"{key_prefix}_heatmap_cols",
        )

    # 3. Auto-suggest title & custom styling expander
    if selected_chart == "Scatter Plot" and x and y:
        default_title = f"{y} vs {x}"
    elif selected_chart == "Bar Chart" and x:
        default_title = f"{y or 'Count'} by {x}"
    elif selected_chart == "Histogram" and x:
        default_title = f"Distribution of {x}"
    elif selected_chart == "Line Chart" and x and y:
        default_title = f"{y} over {x}"
    elif selected_chart == "Correlation Heatmap":
        default_title = "Correlation Heatmap"
    else:
        default_title = f"{selected_chart} Preview"

    with st.expander("⚙️ Chart Options & Title", expanded=False):
        title = st.text_input("Chart Title", value=default_title, key=f"{key_prefix}_title")

    # 4. Construct Configuration & Validate
    config: Dict[str, Any] = {
        "chart_type": selected_chart,
        "x": x,
        "y": y,
        "color": color,
        "agg": agg,
        "bins": bins,
        "columns": columns,
        "title": title or default_title,
    }

    is_valid, error_msg = validate_chart_config(config)
    config["is_valid"] = is_valid
    config["error_message"] = error_msg

    if not is_valid and error_msg:
        st.caption(f"⚠️ {error_msg}")

    return config

