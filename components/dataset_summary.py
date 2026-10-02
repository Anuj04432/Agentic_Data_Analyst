"""
Reusable Dataset Summary KPI component for Agentic Data Analyst.
Extracts high-level dataset metrics and renders 5-column KPI cards.
"""

from typing import Any, Dict, Optional
import pandas as pd
import streamlit as st
from utils.helpers import format_bytes



def extract_summary_metrics(
    df: Optional[pd.DataFrame] = None,
    audit: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Extracts high-level dataset summary metrics from either an active DataFrame
    or a pre-computed audit dictionary from generate_dataset_audit().

    Returns:
        dict with rows, columns, total_cells, missing_cells, missing_pct,
        duplicates, duplicate_pct, memory.
    """
    default_return = {
        "rows": 0,
        "columns": 0,
        "total_cells": 0,
        "missing_cells": 0,
        "missing_pct": 0.0,
        "duplicates": 0,
        "duplicate_pct": 0.0,
        "memory": "0 B",
    }

    # 1. Guard: If both inputs are absent or empty, return default
    if (df is None or df.empty) and (audit is None or not audit):
        return default_return

    # 2. Case A: Extract from pre-computed audit dictionary
    if audit is not None and isinstance(audit, dict):
        shape = audit.get("shape", {})
        rows = int(shape.get("rows", 0))
        columns = int(shape.get("columns", 0))
        total_cells = rows * columns

        # Handle missingness (supports DataFrame or Dict overview)
        missingness = audit.get("missingness", {})
        if isinstance(missingness, pd.DataFrame):
            if not missingness.empty and "Missing Count" in missingness.columns:
                missing_cells = int(missingness["Missing Count"].sum())
            else:
                missing_cells = 0
            missing_pct = round((missing_cells / total_cells) * 100.0, 2) if total_cells > 0 else 0.0
        elif isinstance(missingness, dict):
            missing_cells = int(missingness.get("total_missing_cells", 0))
            missing_pct = float(missingness.get("overall_missing_pct", 0.0))
        else:
            missing_cells = 0
            missing_pct = 0.0

        # Handle duplicates
        duplicates_info = audit.get("duplicates", {})
        if isinstance(duplicates_info, dict):
            duplicates = int(duplicates_info.get("duplicate_count", 0))
            duplicate_pct = float(duplicates_info.get("duplicate_pct", 0.0))
        else:
            duplicates = 0
            duplicate_pct = 0.0

        # Handle memory footprint
        memory_info = audit.get("memory", {})
        if isinstance(memory_info, dict):
            memory_bytes = int(memory_info.get("bytes", 0))
            memory = str(memory_info.get("formatted", format_bytes(memory_bytes)))
        else:
            memory = "0 B"

        return {
            "rows": rows,
            "columns": columns,
            "total_cells": total_cells,
            "missing_cells": missing_cells,
            "missing_pct": missing_pct,
            "duplicates": duplicates,
            "duplicate_pct": duplicate_pct,
            "memory": memory,
        }

    # 3. Case B: Compute directly from DataFrame
    if df is not None and isinstance(df, pd.DataFrame) and not df.empty:
        rows = len(df)
        columns = len(df.columns)
        total_cells = rows * columns

        missing_cells = int(df.isna().sum().sum())
        missing_pct = round((missing_cells / total_cells) * 100.0, 2) if total_cells > 0 else 0.0

        duplicate_rows = int(df.duplicated().sum())
        duplicate_pct = round((duplicate_rows / rows) * 100.0, 2) if rows > 0 else 0.0

        memory_bytes = int(df.memory_usage(deep=True).sum())

        return {
            "rows": rows,
            "columns": columns,
            "total_cells": total_cells,
            "missing_cells": missing_cells,
            "missing_pct": missing_pct,
            "duplicates": duplicate_rows,
            "duplicate_pct": duplicate_pct,
            "memory": format_bytes(memory_bytes),
        }

    return default_return


def render_dataset_summary(
        df: Optional[pd.DataFrame] = None,
        audit: Optional[dict[str,Any]] = None,
        border: bool = True) -> Dict[str,Any]:

    metrices = extract_summary_metrics(df=df, audit=audit)

    if (df is None or df.empty) and (audit is None or metrices["rows"] == 0):
        st.info("ℹ️ No dataset loaded to display summary metrics.")
        return metrices

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        if border:
            with st.container(border=True):
                st.metric(
                    label="📊 Total Rows",
                    value=f"{metrices['rows']:,}",
                    help="Total number of observations / rows in the dataset",
                )
        else:
            st.metric(
                label="📊 Total Rows",
                value=f"{metrices['rows']:,}",
                help="Total number of observations / rows in the dataset",
            )

    with col2:
        if border:
            with st.container(border=True):
                st.metric(
                    label="📐 Total Columns",
                    value=f"{metrices['columns']:,}",
                    help="Total number of columns / features",
                )
        else:
            st.metric(
                label="📐 Total Columns",
                value=f"{metrices['columns']:,}",
                help="Total number of columns / features",
            )

    with col3:
        has_missing = metrices["missing_cells"] > 0
        missing_delta = f"-{metrices['missing_cells']:,} cells" if has_missing else "Clean (0 missing)"
        missing_delta_color = "inverse" if has_missing else "off"

        if border:
            with st.container(border=True):
                st.metric(
                    label="❓ Missing Values",
                    value=f"{metrices['missing_pct']:.1f}%",
                    delta=missing_delta,
                    delta_color=missing_delta_color,
                    help="Percentage and count of missing/NaN cells across all columns",
                )
        else:
            st.metric(
                label="❓ Missing Values",
                value=f"{metrices['missing_pct']:.1f}%",
                delta=missing_delta,
                delta_color=missing_delta_color,
                help="Percentage and count of missing/NaN cells across all columns",
            )

    with col4:
        has_dupes = metrices["duplicates"] > 0
        dupe_delta = f"-{metrices['duplicates']:,} rows" if has_dupes else "Unique (0 dupes)"
        dupe_delta_color = "inverse" if has_dupes else "off"

        if border:
            with st.container(border=True):
                st.metric(
                    label="👥 Duplicate Rows",
                    value=f"{metrices['duplicate_pct']:.1f}%",
                    delta=dupe_delta,
                    delta_color=dupe_delta_color,
                    help="Identical duplicate rows and percentage of dataset",
                )
        else:
            st.metric(
                label="👥 Duplicate Rows",
                value=f"{metrices['duplicate_pct']:.1f}%",
                delta=dupe_delta,
                delta_color=dupe_delta_color,
                help="Identical duplicate rows and percentage of dataset",
            )

    with col5:
        if border:
            with st.container(border=True):
                st.metric(
                    label="💾 Memory Footprint",
                    value=metrices["memory"],
                    help="Deep in-memory DataFrame storage footprint",
                )
        else:
            st.metric(
                label="💾 Memory Footprint",
                value=metrices["memory"],
                help="Deep in-memory DataFrame storage footprint",
            )

    return metrices
