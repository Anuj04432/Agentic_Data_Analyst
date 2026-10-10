"""
Standardized Plotly Chart Builders for the Agentic Data Analyst.

Provides responsive, theme-consistent Plotly figures for exploratory data analysis
and presentation-ready dashboards.
"""

from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


THEME_TEMPLATE = "plotly_white"
DEFAULT_COLOR_PALETTE = px.colors.qualitative.Plotly


def _validate_dataframe(df: Optional[pd.DataFrame]) -> pd.DataFrame:
    """Validates that DataFrame is not None and not empty."""
    if df is None or not isinstance(df, pd.DataFrame) or df.empty:
        raise ValueError("Input DataFrame is empty or None.")
    return df


def _validate_columns(df: pd.DataFrame, columns: List[str]) -> None:
    """Validates that all specified columns exist in the DataFrame."""
    missing = [c for c in columns if c is not None and c not in df.columns]
    if missing:
        raise ValueError(f"Columns not found in dataset: {missing}")


def create_histogram(
    df: pd.DataFrame,
    x: str,
    bins: Optional[int] = 30,
    color: Optional[str] = None,
    title: Optional[str] = None,
    marginal: Optional[str] = None,
) -> go.Figure:
    """
    Builds an interactive histogram for distribution analysis.

    Args:
        df: Input DataFrame.
        x: Column name for distribution.
        bins: Number of histogram bins.
        color: Optional grouping column.
        title: Optional chart title.
        marginal: Optional marginal plot ('box', 'violin', 'rug').

    Returns:
        Plotly Figure object.
    """
    df = _validate_dataframe(df)
    _validate_columns(df, [x] + ([color] if color else []))

    clean_cols = [x] + ([color] if color else [])
    plot_df = df[clean_cols].dropna(subset=[x])

    if plot_df.empty:
        raise ValueError(f"Column '{x}' has no non-null values to plot.")

    nbins = bins if (bins and isinstance(bins, int) and bins > 0) else 30
    chart_title = title or f"Distribution of {x}"

    fig = px.histogram(
        plot_df,
        x=x,
        color=color,
        nbins=nbins,
        marginal=marginal,
        template=THEME_TEMPLATE,
        title=chart_title,
        opacity=0.8,
        color_discrete_sequence=DEFAULT_COLOR_PALETTE,
    )

    fig.update_layout(
        title={"text": f"<b>{chart_title}</b>", "x": 0.02, "xanchor": "left"},
        xaxis_title=x,
        yaxis_title="Count",
        margin=dict(l=40, r=40, t=60, b=40),
        bargap=0.05,
    )
    return fig


def create_boxplot(
    df: pd.DataFrame,
    y: str,
    x: Optional[str] = None,
    color: Optional[str] = None,
    title: Optional[str] = None,
    points: str = "outliers",
) -> go.Figure:
    """
    Builds an interactive box plot for spread, quartile, and outlier analysis.

    Args:
        df: Input DataFrame.
        y: Numeric column name for box plot spread.
        x: Optional categorical column for grouping.
        color: Optional categorical column for color grouping.
        title: Optional chart title.
        points: Outlier points display ('outliers', 'all', False).

    Returns:
        Plotly Figure object.
    """
    df = _validate_dataframe(df)
    cols = [y] + ([x] if x else []) + ([color] if color else [])
    _validate_columns(df, cols)

    plot_df = df[cols].dropna(subset=[y])
    if plot_df.empty:
        raise ValueError(f"Column '{y}' has no non-null numeric values to plot.")

    chart_title = title or (f"{y} by {x}" if x else f"Box Plot of {y}")

    fig = px.box(
        plot_df,
        x=x,
        y=y,
        color=color or x,
        points=points,
        template=THEME_TEMPLATE,
        title=chart_title,
        color_discrete_sequence=DEFAULT_COLOR_PALETTE,
    )

    fig.update_layout(
        title={"text": f"<b>{chart_title}</b>", "x": 0.02, "xanchor": "left"},
        margin=dict(l=40, r=40, t=60, b=40),
    )
    return fig


def create_scatterplot(
    df: pd.DataFrame,
    x: str,
    y: str,
    color: Optional[str] = None,
    title: Optional[str] = None,
    trendline: Optional[str] = None,
) -> go.Figure:
    """
    Builds an interactive scatter plot for bivariate relationship analysis.

    Args:
        df: Input DataFrame.
        x: Numeric column for X-axis.
        y: Numeric column for Y-axis.
        color: Optional grouping column.
        title: Optional chart title.
        trendline: Optional trendline ('ols', None).

    Returns:
        Plotly Figure object.
    """
    df = _validate_dataframe(df)
    cols = [x, y] + ([color] if color else [])
    _validate_columns(df, cols)

    plot_df = df[cols].dropna(subset=[x, y])
    if plot_df.empty:
        raise ValueError(f"Columns '{x}' and '{y}' have no overlapping non-null values to plot.")

    chart_title = title or f"{y} vs {x}"

    try:
        fig = px.scatter(
            plot_df,
            x=x,
            y=y,
            color=color,
            trendline=trendline,
            template=THEME_TEMPLATE,
            title=chart_title,
            opacity=0.75,
            color_discrete_sequence=DEFAULT_COLOR_PALETTE,
        )
    except Exception:
        # Fall back without trendline if statsmodels is unavailable
        fig = px.scatter(
            plot_df,
            x=x,
            y=y,
            color=color,
            template=THEME_TEMPLATE,
            title=chart_title,
            opacity=0.75,
            color_discrete_sequence=DEFAULT_COLOR_PALETTE,
        )

    fig.update_layout(
        title={"text": f"<b>{chart_title}</b>", "x": 0.02, "xanchor": "left"},
        xaxis_title=x,
        yaxis_title=y,
        margin=dict(l=40, r=40, t=60, b=40),
    )
    return fig


def create_barchart(
    df: pd.DataFrame,
    x: str,
    y: Optional[str] = None,
    agg: Optional[str] = "count",
    color: Optional[str] = None,
    title: Optional[str] = None,
    orientation: str = "v",
) -> go.Figure:
    """
    Builds an interactive bar chart supporting counts and metric aggregations.

    Args:
        df: Input DataFrame.
        x: Category column.
        y: Optional numeric column for aggregation.
        agg: Aggregation method ('count', 'mean', 'sum', 'median', 'min', 'max').
        color: Optional color grouping column.
        title: Optional chart title.
        orientation: 'v' for vertical, 'h' for horizontal.

    Returns:
        Plotly Figure object.
    """
    df = _validate_dataframe(df)
    cols = [x] + ([y] if y else []) + ([color] if color else [])
    _validate_columns(df, cols)

    plot_df = df[cols].dropna(subset=[x])
    if plot_df.empty:
        raise ValueError(f"Column '{x}' has no non-null values to plot.")

    agg_method = (agg or "count").lower()

    if y is None or agg_method == "count":
        # Frequency counts
        group_cols = [x] + ([color] if color and color != x else [])
        agg_df = (
            plot_df.groupby(group_cols, observed=False, as_index=False)
            .size()
            .rename(columns={"size": "Count"})
        )
        y_col = "Count"
        chart_title = title or f"Count of {x}"
    else:
        # Numeric aggregation
        plot_df = plot_df.dropna(subset=[y])
        if plot_df.empty:
            raise ValueError(f"Column '{y}' has no non-null values for aggregation.")

        group_cols = [x] + ([color] if color and color != x else [])
        if agg_method == "mean":
            agg_df = plot_df.groupby(group_cols, observed=False, as_index=False)[y].mean()
            metric_label = f"Mean {y}"
        elif agg_method == "sum":
            agg_df = plot_df.groupby(group_cols, observed=False, as_index=False)[y].sum()
            metric_label = f"Total {y}"
        elif agg_method == "median":
            agg_df = plot_df.groupby(group_cols, observed=False, as_index=False)[y].median()
            metric_label = f"Median {y}"
        elif agg_method == "min":
            agg_df = plot_df.groupby(group_cols, observed=False, as_index=False)[y].min()
            metric_label = f"Min {y}"
        elif agg_method == "max":
            agg_df = plot_df.groupby(group_cols, observed=False, as_index=False)[y].max()
            metric_label = f"Max {y}"
        else:
            agg_df = plot_df.groupby(group_cols, observed=False, as_index=False)[y].mean()
            metric_label = f"Mean {y}"

        agg_df = agg_df.rename(columns={y: metric_label})
        y_col = metric_label
        chart_title = title or f"{metric_label} by {x}"

    # Sort categories by value descending if no color grouping for clean display
    if not color or color == x:
        agg_df = agg_df.sort_values(by=y_col, ascending=False).head(30)

    if orientation == "h":
        fig = px.bar(
            agg_df,
            x=y_col,
            y=x,
            color=color if color != x else None,
            orientation="h",
            template=THEME_TEMPLATE,
            title=chart_title,
            color_discrete_sequence=DEFAULT_COLOR_PALETTE,
        )
    else:
        fig = px.bar(
            agg_df,
            x=x,
            y=y_col,
            color=color if color != x else None,
            template=THEME_TEMPLATE,
            title=chart_title,
            color_discrete_sequence=DEFAULT_COLOR_PALETTE,
        )

    fig.update_layout(
        title={"text": f"<b>{chart_title}</b>", "x": 0.02, "xanchor": "left"},
        margin=dict(l=40, r=40, t=60, b=40),
    )
    return fig


def create_linechart(
    df: pd.DataFrame,
    x: str,
    y: str,
    color: Optional[str] = None,
    title: Optional[str] = None,
    markers: bool = True,
) -> go.Figure:
    """
    Builds an interactive line chart for sequential and time-series trends.

    Args:
        df: Input DataFrame.
        x: Date or sequential feature.
        y: Numeric feature for Y-axis.
        color: Optional grouping column.
        title: Optional chart title.
        markers: Whether to show markers on line points.

    Returns:
        Plotly Figure object.
    """
    df = _validate_dataframe(df)
    cols = [x, y] + ([color] if color else [])
    _validate_columns(df, cols)

    plot_df = df[cols].dropna(subset=[x, y]).copy()
    if plot_df.empty:
        raise ValueError(f"Columns '{x}' and '{y}' have no overlapping non-null values to plot.")

    # Sort by X to avoid jagged zig-zag lines
    try:
        plot_df = plot_df.sort_values(by=x)
    except Exception:
        pass

    chart_title = title or f"{y} over {x}"

    fig = px.line(
        plot_df,
        x=x,
        y=y,
        color=color,
        markers=markers,
        template=THEME_TEMPLATE,
        title=chart_title,
        color_discrete_sequence=DEFAULT_COLOR_PALETTE,
    )

    fig.update_layout(
        title={"text": f"<b>{chart_title}</b>", "x": 0.02, "xanchor": "left"},
        xaxis_title=x,
        yaxis_title=y,
        margin=dict(l=40, r=40, t=60, b=40),
    )
    return fig


def create_piechart(
    df: pd.DataFrame,
    names: str,
    values: Optional[str] = None,
    title: Optional[str] = None,
    hole: float = 0.4,
    max_slices: int = 10,
) -> go.Figure:
    """
    Builds an interactive pie or donut chart for proportional shares.

    Args:
        df: Input DataFrame.
        names: Categorical column name.
        values: Optional numeric column for slice values.
        title: Optional chart title.
        hole: Inner cutout radius (0.0 for Pie, > 0.0 for Donut).
        max_slices: Maximum number of distinct slices before aggregating into 'Other'.

    Returns:
        Plotly Figure object.
    """
    df = _validate_dataframe(df)
    cols = [names] + ([values] if values else [])
    _validate_columns(df, cols)

    plot_df = df[cols].dropna(subset=[names])
    if plot_df.empty:
        raise ValueError(f"Column '{names}' has no non-null values to plot.")

    if values is None:
        agg_df = (
            plot_df.groupby(names, observed=False, as_index=False)
            .size()
            .rename(columns={"size": "Value"})
        )
        val_col = "Value"
    else:
        plot_df = plot_df.dropna(subset=[values])
        if plot_df.empty:
            raise ValueError(f"Column '{values}' has no non-null values for slice weights.")
        agg_df = (
            plot_df.groupby(names, observed=False, as_index=False)[values]
            .sum()
            .rename(columns={values: "Value"})
        )
        val_col = "Value"

    # Limit to top slices to prevent messy slices
    if len(agg_df) > max_slices:
        top_df = agg_df.sort_values(by=val_col, ascending=False).head(max_slices - 1)
        other_val = agg_df.sort_values(by=val_col, ascending=False).iloc[max_slices - 1 :][val_col].sum()
        other_row = pd.DataFrame([{names: "Other", val_col: other_val}])
        agg_df = pd.concat([top_df, other_row], ignore_index=True)

    chart_title = title or f"Share of {names}"

    fig = px.pie(
        agg_df,
        names=names,
        values=val_col,
        hole=hole,
        template=THEME_TEMPLATE,
        title=chart_title,
        color_discrete_sequence=DEFAULT_COLOR_PALETTE,
    )

    fig.update_traces(textposition="inside", textinfo="percent+label")
    fig.update_layout(
        title={"text": f"<b>{chart_title}</b>", "x": 0.02, "xanchor": "left"},
        margin=dict(l=40, r=40, t=60, b=40),
    )
    return fig


def create_correlation_heatmap(
    df: pd.DataFrame,
    columns: Optional[List[str]] = None,
    method: str = "pearson",
    title: Optional[str] = None,
) -> go.Figure:
    """
    Builds an interactive correlation heatmap for numeric relationships.

    Args:
        df: Input DataFrame.
        columns: Optional subset of numeric column names.
        method: Correlation method ('pearson', 'spearman', 'kendall').
        title: Optional chart title.

    Returns:
        Plotly Figure object.
    """
    df = _validate_dataframe(df)

    if columns:
        _validate_columns(df, columns)
        num_df = df[columns].select_dtypes(include="number")
    else:
        num_df = df.select_dtypes(include="number")

    if num_df.shape[1] < 2:
        raise ValueError("At least 2 numeric columns with variance are required for correlation heatmap.")

    corr = num_df.corr(method=method).round(2)
    chart_title = title or f"Correlation Heatmap ({method.capitalize()})"

    fig = px.imshow(
        corr,
        text_auto=".2f",
        aspect="auto",
        color_continuous_scale="RdBu_r",
        zmin=-1,
        zmax=1,
        template=THEME_TEMPLATE,
        title=chart_title,
    )

    fig.update_layout(
        title={"text": f"<b>{chart_title}</b>", "x": 0.02, "xanchor": "left"},
        margin=dict(l=40, r=40, t=60, b=40),
    )
    return fig


def build_chart_from_config(df: pd.DataFrame, config: Dict[str, Any]) -> go.Figure:
    """
    Master dispatcher: constructs a Plotly Figure from a standardized ChartConfig dictionary.

    Args:
        df: Input DataFrame.
        config: ChartConfig dictionary with keys:
            - chart_type: 'Bar Chart', 'Line Chart', 'Scatter Plot', 'Histogram',
                          'Box Plot', 'Pie / Donut Chart', 'Correlation Heatmap'
            - x: primary X-axis column
            - y: primary Y-axis column
            - color: grouping column (optional)
            - agg: aggregation method (optional)
            - bins: histogram bin count (optional)
            - columns: heatmap column list (optional)
            - title: custom title (optional)

    Returns:
        Rendered Plotly Figure object.

    Raises:
        ValueError: If config is invalid or chart_type is unsupported.
    """
    df = _validate_dataframe(df)

    if not isinstance(config, dict) or not config:
        raise ValueError("Chart configuration dictionary is empty or missing.")

    chart_type = config.get("chart_type")
    x = config.get("x")
    y = config.get("y")
    color = config.get("color")
    agg = config.get("agg")
    bins = config.get("bins")
    columns = config.get("columns")
    title = config.get("title")

    if chart_type == "Histogram":
        return create_histogram(df, x=x, bins=bins, color=color, title=title)

    elif chart_type == "Box Plot":
        # Box plot can use y as primary metric, or x if y is None
        metric_col = y or x
        group_col = x if (y and x != y) else None
        return create_boxplot(df, y=metric_col, x=group_col, color=color, title=title)

    elif chart_type == "Scatter Plot":
        return create_scatterplot(df, x=x, y=y, color=color, title=title)

    elif chart_type == "Bar Chart":
        return create_barchart(df, x=x, y=y, agg=agg, color=color, title=title)

    elif chart_type == "Line Chart":
        return create_linechart(df, x=x, y=y, color=color, title=title)

    elif chart_type == "Pie / Donut Chart":
        return create_piechart(df, names=x, values=y, title=title)

    elif chart_type == "Correlation Heatmap":
        return create_correlation_heatmap(df, columns=columns, title=title)

    else:
        raise ValueError(f"Unsupported chart type '{chart_type}'.")
