"""
Intelligent Rule-Based Chart Recommender for the Agentic Data Analyst.

Inspects dataset column types, cardinality, and distribution patterns to automatically
suggest the most informative visualizations for exploratory analysis.
"""

from typing import Any, Dict, List, Optional
import pandas as pd
from components.column_selector import classify_columns


def recommend_charts(
    df: Optional[pd.DataFrame],
    max_recommendations: int = 4,
) -> List[Dict[str, Any]]:
    """
    Evaluates dataset schema and properties to return prioritized chart recommendations.

    Args:
        df: Input pandas DataFrame to inspect.
        max_recommendations: Maximum number of recommendations to return (default: 4).

    Returns:
        List of recommendation dictionaries, each containing:
            - chart_type: Standard chart type string
            - x: Column name for X-axis
            - y: Column name for Y-axis (or None)
            - color: Column name for color grouping (or None)
            - agg: Aggregation method ('mean', 'sum', 'count', etc.)
            - bins: Bins count for histograms
            - columns: Feature list for heatmaps
            - title: Suggested presentation title
            - reason: Analytical rationale for the recommendation
            - icon: Emoji icon for UI display
            - priority: Integer rank (lower = higher priority)
    """
    if df is None or not isinstance(df, pd.DataFrame) or df.empty:
        return []

    col_types = classify_columns(df)
    num_cols = col_types.get("numeric", [])
    cat_cols = col_types.get("categorical", [])
    date_cols = col_types.get("datetime", [])
    bool_cols = col_types.get("boolean", [])

    discrete_cols = cat_cols + bool_cols
    recommendations: List[Dict[str, Any]] = []

    # Helper to check unique count safely
    def _unique_count(col: str) -> int:
        try:
            return df[col].nunique(dropna=True)
        except Exception:
            return 0

    # 1. Temporal Trend (Line Chart)
    if date_cols and num_cols:
        date_col = date_cols[0]
        num_col = num_cols[0]
        recommendations.append({
            "chart_type": "Line Chart",
            "x": date_col,
            "y": num_col,
            "color": None,
            "agg": None,
            "bins": None,
            "columns": [],
            "title": f"{num_col} over {date_col}",
            "reason": f"Track temporal trends, seasonality, and time fluctuations for '{num_col}'.",
            "icon": "📈",
            "priority": 1,
        })

    # 2. Bivariate Relationship (Scatter Plot)
    if len(num_cols) >= 2:
        x_col = num_cols[0]
        y_col = num_cols[1]

        # Pick pair with notable variance or correlation if available
        try:
            corr_sub = df[num_cols[:5]].corr().abs()
            np_pairs = []
            cols = corr_sub.columns
            for i in range(len(cols)):
                for j in range(i + 1, len(cols)):
                    val = corr_sub.iloc[i, j]
                    if pd.notna(val):
                        np_pairs.append((val, cols[i], cols[j]))
            if np_pairs:
                np_pairs.sort(reverse=True)
                top_pair = np_pairs[0]
                x_col, y_col = top_pair[1], top_pair[2]
        except Exception:
            pass

        color_col = discrete_cols[0] if (discrete_cols and _unique_count(discrete_cols[0]) <= 8) else None
        recommendations.append({
            "chart_type": "Scatter Plot",
            "x": x_col,
            "y": y_col,
            "color": color_col,
            "agg": None,
            "bins": None,
            "columns": [],
            "title": f"{y_col} vs {x_col}",
            "reason": f"Evaluate correlation and cluster patterns between '{x_col}' and '{y_col}'.",
            "icon": "🔵",
            "priority": 2,
        })

    # 3. Categorical Metric Comparison (Bar Chart)
    eligible_cats = [c for c in discrete_cols if 2 <= _unique_count(c) <= 20]
    if eligible_cats:
        cat_col = eligible_cats[0]
        if num_cols:
            num_col = num_cols[0]
            recommendations.append({
                "chart_type": "Bar Chart",
                "x": cat_col,
                "y": num_col,
                "color": None,
                "agg": "mean",
                "bins": None,
                "columns": [],
                "title": f"Average {num_col} by {cat_col}",
                "reason": f"Compare average '{num_col}' across different '{cat_col}' segments.",
                "icon": "📊",
                "priority": 3,
            })
        else:
            recommendations.append({
                "chart_type": "Bar Chart",
                "x": cat_col,
                "y": None,
                "color": None,
                "agg": "count",
                "bins": None,
                "columns": [],
                "title": f"Frequency Breakdown of {cat_col}",
                "reason": f"Visualize frequency counts across '{cat_col}' categories.",
                "icon": "📊",
                "priority": 3,
            })

    # 4. Continuous Feature Distribution (Histogram)
    if num_cols:
        target_num = num_cols[0]
        # Choose column with highest variance or non-zero spread
        try:
            stds = df[num_cols].std().dropna()
            if not stds.empty:
                target_num = stds.idxmax()
        except Exception:
            pass

        recommendations.append({
            "chart_type": "Histogram",
            "x": target_num,
            "y": None,
            "color": None,
            "agg": None,
            "bins": 30,
            "columns": [],
            "title": f"Distribution of {target_num}",
            "reason": f"Examine distribution shape, spread, and skewness for '{target_num}'.",
            "icon": "📉",
            "priority": 4,
        })

    # 5. Low-Cardinality Proportions (Pie / Donut Chart)
    low_card_cats = [c for c in discrete_cols if 2 <= _unique_count(c) <= 6]
    if low_card_cats:
        cat_col = low_card_cats[0]
        recommendations.append({
            "chart_type": "Pie / Donut Chart",
            "x": cat_col,
            "y": None,
            "color": None,
            "agg": "count",
            "bins": None,
            "columns": [],
            "title": f"{cat_col} Proportions",
            "reason": f"Show proportional composition for distinct '{cat_col}' groups.",
            "icon": "🍩",
            "priority": 5,
        })

    # 6. Multivariate Correlation Matrix (Correlation Heatmap)
    if len(num_cols) >= 3:
        heatmap_features = num_cols[: min(8, len(num_cols))]
        recommendations.append({
            "chart_type": "Correlation Heatmap",
            "x": None,
            "y": None,
            "color": None,
            "agg": None,
            "bins": None,
            "columns": heatmap_features,
            "title": "Feature Correlation Heatmap",
            "reason": f"Scan pairwise linear correlations across {len(heatmap_features)} numeric features.",
            "icon": "🔥",
            "priority": 6,
        })

    # 7. Spread & Outliers (Box Plot)
    if num_cols:
        num_col = num_cols[0]
        group_col = eligible_cats[0] if eligible_cats else None
        recommendations.append({
            "chart_type": "Box Plot",
            "x": group_col,
            "y": num_col,
            "color": None,
            "agg": None,
            "bins": None,
            "columns": [],
            "title": f"{num_col} Spread" + (f" by {group_col}" if group_col else ""),
            "reason": f"Detect outlier points and compare quartile ranges for '{num_col}'.",
            "icon": "📦",
            "priority": 7,
        })

    # Sort recommendations by priority and deduplicate by (chart_type, x, y)
    seen = set()
    deduped: List[Dict[str, Any]] = []
    recommendations.sort(key=lambda r: r["priority"])

    for rec in recommendations:
        key = (rec["chart_type"], rec.get("x"), rec.get("y"))
        if key not in seen:
            seen.add(key)
            deduped.append(rec)

    return deduped[:max_recommendations]
