"""
Exploratory Data Analysis (EDA) View for Agentic Data Analyst.
Phase 4 Implementation: Assembles pure analytical engines and modular UI components
into an interactive diagnostic and data remediation dashboard.
"""

from typing import Any, Dict, List, Optional, Union
import html
import numpy as np
import pandas as pd
import streamlit as st

# Analysis engines
from analysis.correlations import (
    calculate_correlation_matrix,
    get_correlation_overview,
    get_target_correlations,
    get_top_correlations,
)
from analysis.duplicates import (
    drop_duplicates_clean,
    get_duplicate_summary,
)
from analysis.missing_values import (
    get_missing_summary,
    get_missingness_overview,
    impute_missing_values,
)
from analysis.outliers import (
    cap_outliers,
    drop_outliers,
    get_outliers_summary,
)
from analysis.profiling import (
    calculate_health_score,
    generate_dataset_audit,
)
from analysis.statistics import (
    get_categorical_summary,
    get_distribution_stats,
    get_numeric_summary,
)

# Modular UI components
from components.analysis_result import (
    render_actionable_warnings,
    render_correlation_badge,
    render_distribution_badge,
    render_health_score_card,
)
from components.column_selector import classify_columns
from components.data_preview import render_data_preview
from components.dataset_summary import render_dataset_summary
from utils.session_state import get_dataset, set_dataset

# Optional Plotly support for heatmaps
try:
    import plotly.express as px
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False


# ==============================================================================
# SUB-TAB RENDERERS
# ==============================================================================


def _render_overview_tab(df: pd.DataFrame) -> None:
    """Render Sub-Tab A: Data Overview, Interactive Preview, and Data Dictionary."""
    st.markdown("#### 🔍 Interactive Data Preview")
    render_data_preview(df, default_page_size=25, key_prefix="eda_preview")

    st.markdown("---")
    st.markdown("#### 📖 Column Data Dictionary")
    st.caption("Detailed structural metadata, data types, and fill rates across all features.")

    col_types_dict = classify_columns(df)
    total_rows = len(df)

    dict_rows = []
    for col in df.columns:
        series = df[col]
        non_null = int(series.notna().sum())
        null_count = int(series.isna().sum())
        fill_rate = round((non_null / total_rows) * 100.0, 1) if total_rows > 0 else 0.0
        unique_count = int(series.nunique(dropna=True))

        # Detect analytical category
        if col in col_types_dict.get("numeric", []):
            analytical_type = "Numeric"
        elif col in col_types_dict.get("datetime", []):
            analytical_type = "Datetime"
        elif col in col_types_dict.get("boolean", []):
            analytical_type = "Boolean"
        else:
            analytical_type = "Categorical"

        # Distinct sample preview
        sample_vals = series.dropna().unique()[:3]
        sample_str = ", ".join(str(v) for v in sample_vals) if len(sample_vals) > 0 else "N/A"
        if len(sample_str) > 50:
            sample_str = sample_str[:47] + "..."

        dict_rows.append({
            "Column Name": col,
            "Analytical Type": analytical_type,
            "Data Type (dtype)": str(series.dtype),
            "Non-Null Count": f"{non_null:,}",
            "Missing Count": f"{null_count:,}",
            "Fill Rate (%)": f"{fill_rate:.1f}%",
            "Unique Values": f"{unique_count:,}",
            "Sample Values": sample_str,
        })

    dictionary_df = pd.DataFrame(dict_rows)
    st.dataframe(dictionary_df, use_container_width=True, hide_index=True)


def _render_missing_and_duplicates_tab(df: pd.DataFrame, filename: str) -> None:
    """Render Sub-Tab B: Missing Values Diagnostics, Imputation Panel, and Deduplication."""
    st.markdown("#### ❓ Missing Values Analysis")
    missing_summary = get_missing_summary(df)
    missing_overview = get_missingness_overview(df)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Missing Cells", f"{missing_overview['total_missing_cells']:,}")
    with col2:
        st.metric("Overall Missing %", f"{missing_overview['overall_missing_pct']:.2f}%")
    with col3:
        st.metric("Columns with Missing", f"{missing_overview['columns_with_missing_count']} / {len(df.columns)}")

    if missing_overview["total_missing_cells"] == 0:
        st.success("🎉 **Clean Dataset**: No missing values detected in any column!")
    else:
        st.dataframe(
            missing_summary,
            use_container_width=True,
            hide_index=True,
        )

        st.markdown("---")
        st.markdown("##### 🛠️ Interactive Imputation & Cleaning Panel")
        st.caption("Apply automated or targeted strategies to impute missing cells. Changes update the active session.")

        cols_with_missing = missing_overview["columns_with_missing"]
        target_scope = st.radio(
            "Target Scope",
            options=["Specific Column", "All Numeric Columns", "Entire Dataset (Auto Strategy)"],
            horizontal=True,
            key="impute_target_scope",
        )

        new_df = None
        if target_scope == "Specific Column":
            target_col = st.selectbox(
                "Select Column to Impute",
                options=cols_with_missing if cols_with_missing else list(df.columns),
                key="impute_col_select",
            )
            is_numeric = pd.api.types.is_numeric_dtype(df[target_col])
            strategy_options = ["Median", "Mean", "Mode", "Custom Constant", "Drop Rows with Missing"] if is_numeric else ["Mode", "Custom Constant", "Drop Rows with Missing"]
            selected_strategy = st.selectbox("Imputation Strategy", options=strategy_options, key="impute_strat_col")

            fill_val = None
            if selected_strategy == "Custom Constant":
                fill_val = st.text_input("Enter replacement value", value="0" if is_numeric else "Unknown", key="impute_custom_val")

            if st.button("🚀 Apply Column Imputation", type="primary", key="btn_apply_col_impute"):
                clean_df = df.copy()
                if selected_strategy == "Mean":
                    mean_val = clean_df[target_col].mean()
                    clean_df[target_col] = clean_df[target_col].fillna(mean_val)
                elif selected_strategy == "Median":
                    med_val = clean_df[target_col].median()
                    clean_df[target_col] = clean_df[target_col].fillna(med_val)
                elif selected_strategy == "Mode":
                    mode_series = clean_df[target_col].mode(dropna=True)
                    if not mode_series.empty:
                        clean_df[target_col] = clean_df[target_col].fillna(mode_series.iloc[0])
                elif selected_strategy == "Custom Constant":
                    val_to_use = float(fill_val) if is_numeric and fill_val.replace('.', '', 1).isdigit() else fill_val
                    clean_df[target_col] = clean_df[target_col].fillna(val_to_use)
                elif selected_strategy == "Drop Rows with Missing":
                    clean_df = clean_df.dropna(subset=[target_col]).reset_index(drop=True)

                set_dataset(clean_df, filename)
                st.toast(f"Imputed missing values for column '{target_col}'!", icon="✨")
                st.rerun()

        elif target_scope == "All Numeric Columns":
            num_strat = st.selectbox("Strategy for Numeric Columns", options=["Median", "Mean"], key="impute_num_strat")
            if st.button("🚀 Apply Numeric Imputation", type="primary", key="btn_apply_num_impute"):
                clean_df = impute_missing_values(df, strategy=num_strat.lower())
                set_dataset(clean_df, filename)
                st.toast(f"Imputed all numeric columns with {num_strat}!", icon="✨")
                st.rerun()

        else:  # Entire Dataset
            st.info("Auto strategy applies **Median** for numerical columns and **Mode** for categorical columns.")
            if st.button("🚀 Apply Auto Imputation", type="primary", key="btn_apply_auto_impute"):
                clean_df = impute_missing_values(df, strategy="auto")
                set_dataset(clean_df, filename)
                st.toast("Applied automated dataset imputation!", icon="✨")
                st.rerun()

    # Section 2: Duplicates
    st.markdown("---")
    st.markdown("#### 👥 Duplicate Rows Inspection & Deduplication")
    dup_summary = get_duplicate_summary(df)

    d_col1, d_col2 = st.columns(2)
    with d_col1:
        st.metric("Duplicate Rows Count", f"{dup_summary['duplicate_count']:,}")
    with d_col2:
        st.metric("Duplicate Percentage", f"{dup_summary['duplicate_pct']:.2f}%")

    if not dup_summary["has_duplicates"]:
        st.success("✅ **Clean Dataset**: No duplicate rows found.")
    else:
        st.warning(f"⚠️ Found **{dup_summary['duplicate_count']:,} duplicate rows** ({dup_summary['duplicate_pct']:.2f}% of total).")
        with st.expander("👁️ Inspect Duplicate Records", expanded=False):
            st.dataframe(dup_summary["duplicate_rows"], use_container_width=True)

        dedup_col1, dedup_col2 = st.columns([2, 1])
        with dedup_col1:
            keep_rule = st.selectbox(
                "Deduplication Rule",
                options=["first", "last", "drop_all"],
                format_func=lambda x: "Keep First Occurrence ('first')" if x == "first" else ("Keep Last Occurrence ('last')" if x == "last" else "Drop All Duplicates ('drop_all')"),
                key="dedup_keep_rule",
            )
        with dedup_col2:
            st.write("")
            st.write("")
            if st.button("🗑️ Remove Duplicate Rows", type="primary", key="btn_dedup"):
                clean_df, removed_count = drop_duplicates_clean(df, keep=keep_rule)
                set_dataset(clean_df, filename)
                st.toast(f"Successfully removed {removed_count:,} duplicate rows!", icon="🗑️")
                st.rerun()


def _render_distributions_and_outliers_tab(df: pd.DataFrame, filename: str) -> None:
    """Render Sub-Tab C: Descriptive Stats, Skewness/Kurtosis, and Outlier Remediation."""
    st.markdown("#### 📊 Summary Statistics & Distribution Shapes")
    num_summary = get_numeric_summary(df)
    cat_summary = get_categorical_summary(df)

    stat_type = st.radio("Feature Type", options=["Numeric Features", "Categorical Features"], horizontal=True, key="eda_stat_type")

    if stat_type == "Numeric Features":
        if num_summary.empty:
            st.info("ℹ️ No numeric features present in this dataset.")
        else:
            st.dataframe(num_summary, use_container_width=True, hide_index=True)

            # Deep-dive inspector for distribution shape
            st.markdown("##### 🔬 Feature Distribution Shape Inspector")
            num_cols = df.select_dtypes(include="number").columns.tolist()
            inspected_col = st.selectbox("Select numeric feature to inspect", options=num_cols, key="eda_inspect_col")

            if inspected_col:
                series = df[inspected_col]
                dist_stats = get_distribution_stats(series)

                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    st.metric("Skewness", f"{dist_stats['skewness']}")
                with c2:
                    st.markdown("**Shape Category**")
                    render_distribution_badge(dist_stats["skew_interpretation"])
                with c3:
                    st.metric("Kurtosis", f"{dist_stats['kurtosis']}")
                with c4:
                    st.markdown("**Tail Weight**")
                    st.caption(f"{dist_stats['kurt_interpretation']}")
    else:
        if cat_summary.empty:
            st.info("ℹ️ No categorical features present in this dataset.")
        else:
            st.dataframe(cat_summary, use_container_width=True, hide_index=True)

    # Outlier Analysis Section
    st.markdown("---")
    st.markdown("#### 🚨 Outlier Detection & Treatment Panel")
    outlier_method = st.radio("Detection Methodology", options=["IQR (Tukey's 1.5× Rule)", "Z-Score (Threshold = 3.0)"], horizontal=True, key="eda_outlier_method")
    method_key = "iqr" if "IQR" in outlier_method else "zscore"

    outliers_df = get_outliers_summary(df, method=method_key)
    if outliers_df.empty:
        st.info("ℹ️ No numeric features available for outlier detection.")
    else:
        has_any_outliers = (outliers_df["Outlier Count"] > 0).any()
        if not has_any_outliers:
            st.success("✅ **No Outliers Detected**: All numerical values fall within expected statistical boundaries.")
        else:
            st.dataframe(outliers_df, use_container_width=True, hide_index=True)

            st.markdown("##### 🩹 Interactive Outlier Treatment")
            st.caption("Treat extreme anomalies to prevent model skewness. Choose Winsorization (capping) or row deletion.")

            cols_with_outliers = outliers_df[outliers_df["Outlier Count"] > 0]["Column"].tolist()
            t_col1, t_col2, t_col3 = st.columns(3)

            with t_col1:
                target_outlier_col = st.selectbox(
                    "Select Feature to Treat",
                    options=cols_with_outliers if cols_with_outliers else outliers_df["Column"].tolist(),
                    key="outlier_target_col",
                )
            with t_col2:
                action_choice = st.selectbox(
                    "Treatment Action",
                    options=[
                        "Winsorization (Cap to IQR Bounds)",
                        "Drop Outlier Rows (This Column)",
                        "Drop Outlier Rows (All Numeric Columns)",
                    ],
                    key="outlier_action_choice",
                )
            with t_col3:
                iqr_factor = st.slider("IQR Factor", min_value=1.0, max_value=3.0, value=1.5, step=0.25, key="outlier_iqr_factor")

            if st.button("🚀 Apply Outlier Treatment", type="primary", key="btn_apply_outlier"):
                if "Winsorization" in action_choice:
                    clean_df, affected_count = cap_outliers(df, target_outlier_col, factor=iqr_factor)
                    set_dataset(clean_df, filename)
                    st.toast(f"Capped {affected_count:,} outliers in '{target_outlier_col}'!", icon="🩹")
                    st.rerun()
                elif "This Column" in action_choice:
                    clean_df, affected_count = drop_outliers(df, columns=[target_outlier_col], factor=iqr_factor)
                    set_dataset(clean_df, filename)
                    st.toast(f"Removed {affected_count:,} outlier rows from '{target_outlier_col}'!", icon="🗑️")
                    st.rerun()
                else:
                    clean_df, affected_count = drop_outliers(df, factor=iqr_factor)
                    set_dataset(clean_df, filename)
                    st.toast(f"Removed {affected_count:,} rows with outliers across all features!", icon="🗑️")
                    st.rerun()


def _render_correlations_tab(df: pd.DataFrame) -> None:
    """Render Sub-Tab D: Correlation Matrix, Heatmap, Top Pairs, and Multicollinearity."""
    st.markdown("#### 🔗 Correlation Matrix & Relationship Analysis")

    method_choice = st.selectbox("Correlation Method", options=["pearson", "spearman", "kendall"], format_func=lambda x: f"{x.capitalize()} Correlation", key="eda_corr_method")
    corr_matrix = calculate_correlation_matrix(df, method=method_choice)

    if corr_matrix.empty:
        st.info("ℹ️ At least two numeric columns with variance are required to compute correlations.")
        return

    # Visual Correlation Heatmap
    if HAS_PLOTLY:
        fig = px.imshow(
            corr_matrix,
            text_auto=".2f",
            aspect="auto",
            color_continuous_scale="RdBu_r",
            zmin=-1.0,
            zmax=1.0,
            labels=dict(color="Correlation"),
        )
        fig.update_layout(
            title=f"Correlation Heatmap ({method_choice.capitalize()})",
            margin=dict(l=40, r=40, t=50, b=40),
            height=500,
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.dataframe(
            corr_matrix.style.background_gradient(cmap="coolwarm", vmin=-1.0, vmax=1.0).format("{:.2f}"),
            use_container_width=True,
        )

    # Multicollinearity Assessment
    st.markdown("---")
    st.markdown("#### 🚨 Multicollinearity Assessment")
    corr_overview = get_correlation_overview(df, threshold=0.85)

    if corr_overview.get("has_high_multicollinearity"):
        st.warning(
            f"⚠️ **High Multicollinearity Warning**: Detected {corr_overview['high_correlation_count']} feature pair(s) "
            "with correlation $|r| \\ge 0.85$. Severe multicollinearity inflates variance in linear models. "
            "Consider dropping or engineering redundant features."
        )
    else:
        st.success("✅ **Low Collinearity**: No critical multicollinearity ($|r| \\ge 0.85$) detected among numerical features.")

    # Top Correlated Feature Pairs
    st.markdown("---")
    st.markdown("#### 🌟 Top Correlated Feature Pairs")

    c1, c2 = st.columns([2, 1])
    with c1:
        corr_thresh = st.slider("Correlation Threshold (|r| ≥)", min_value=0.0, max_value=1.0, value=0.4, step=0.05, key="eda_corr_thresh")
    with c2:
        top_n = st.slider("Max Pairs to Display", min_value=5, max_value=50, value=15, step=5, key="eda_top_n_pairs")

    top_corrs = get_top_correlations(df, threshold=corr_thresh, top_n=top_n, method=method_choice)
    if top_corrs.empty:
        st.info(f"ℹ️ No feature pairs with correlation magnitude $\\ge {corr_thresh:.2f}$.")
    else:
        st.dataframe(top_corrs, use_container_width=True, hide_index=True)

    # Target Feature Correlations
    st.markdown("---")
    with st.expander("🎯 Target Feature Association Analysis", expanded=False):
        st.caption("Calculate linear or rank correlation of all numeric features against a designated target variable.")
        num_cols = df.select_dtypes(include="number").columns.tolist()
        target_col = st.selectbox("Select Target Variable", options=num_cols, key="eda_target_col")

        if target_col:
            target_corrs = get_target_correlations(df, target_column=target_col, method=method_choice)
            if target_corrs.empty:
                st.info("ℹ️ No other numeric features available to correlate against the target.")
            else:
                st.dataframe(target_corrs, use_container_width=True, hide_index=True)


# ==============================================================================
# MAIN TAB ENTRY POINT
# ==============================================================================


def analysis_tab(df_or_file: Optional[Union[pd.DataFrame, Any]] = None) -> None:
    """
    Main entry point for Tab 1: Exploratory Data Analysis (EDA).
    Seamlessly resolves the active dataset from parameter or session state,
    renders the Top Hero Section (Health score, KPIs, diagnostic alerts),
    and mounts the 4 comprehensive analytical sub-tabs.

    Args:
        df_or_file: Optional DataFrame or file handle. If None, resolves from session state.
    """
    # 1. Resolve DataFrame and Filename
    df = None
    filename = "Active Dataset"

    if isinstance(df_or_file, pd.DataFrame):
        df = df_or_file
        _, stored_filename = get_dataset()
        if stored_filename:
            filename = stored_filename
    else:
        stored_df, stored_filename = get_dataset()
        if stored_df is not None:
            df = stored_df
            filename = stored_filename or "Active Dataset"

    # 2. Empty-State Guard
    if df is None or df.empty:
        st.info("ℹ️ **No dataset loaded.** Please upload a dataset or select a sample dataset from the sidebar to begin analysis.")
        return

    # 3. Top Hero Section
    st.markdown("## 📊 Exploratory Data Analysis")
    st.caption(f"Comprehensive diagnostic profiling for **{filename}** ({df.shape[0]:,} rows × {df.shape[1]} columns)")

    # Dataset Health Card
    health_data = calculate_health_score(df)
    render_health_score_card(health_data, border=True)

    # KPI Summary Metric Strip
    render_dataset_summary(df=df, border=True)

    # Actionable Warnings & Diagnostic Alerts Expander
    audit = generate_dataset_audit(df)
    render_actionable_warnings(audit.get("warnings", []), expanded=False)

    st.markdown("---")

    # 4. Mount Sub-Tabs Container
    tab_overview, tab_missing_dup, tab_distributions, tab_correlations = st.tabs([
        "📋 Data Overview & Preview",
        "❓ Missing Values & Duplicates",
        "📊 Distributions & Outliers",
        "🔗 Correlations & Relationships",
    ])

    with tab_overview:
        _render_overview_tab(df)

    with tab_missing_dup:
        _render_missing_and_duplicates_tab(df, filename)

    with tab_distributions:
        _render_distributions_and_outliers_tab(df, filename)

    with tab_correlations:
        _render_correlations_tab(df)