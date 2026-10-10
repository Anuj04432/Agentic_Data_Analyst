"""
Interactive Data Visualization Tab for the Agentic Data Analyst.

Integrates standardized Plotly builders, rule-based recommendations,
and the modular chart selector component.
"""

from typing import Any, Dict, Optional
import io
import pandas as pd
import streamlit as st

from components.chart_selector import render_chart_selector, validate_chart_config
from utils.session_state import get_dataset
from visualization.charts import build_chart_from_config
from visualization.chart_recommender import recommend_charts


def visualization_tab(df: Optional[pd.DataFrame] = None) -> None:
    """
    Renders the Data Visualization dashboard tab.

    Args:
        df: Optional pandas DataFrame. If None, retrieves the active dataset
            from session state.
    """
    if df is None:
        df, _ = get_dataset()

    if df is None or df.empty:
        st.info("👋 **No dataset active.** Please upload a dataset or pick a sample from the sidebar to visualize.")
        return

    st.markdown("### 📈 Interactive Data Visualization Studio")
    st.caption("Generate publication-ready Plotly charts, explore trends, or choose from automated recommendations.")

    # Section 1: Automated Smart Chart Recommendations
    _render_recommendations_section(df)

    st.markdown("---")

    # Section 2: Custom Chart Builder & Configuration
    st.markdown("#### 🎨 Chart Builder & Dimension Mapping")

    # Check if a recommendation preset was selected
    active_preset = st.session_state.get("active_viz_preset")
    if active_preset:
        c1, c2 = st.columns([3, 1])
        with c1:
            st.info(f"⚡ Currently viewing recommended preset: **{active_preset.get('title', 'Custom Chart')}** ({active_preset.get('chart_type')})")
        with c2:
            if st.button("🔄 Reset to Manual Builder", key="btn_reset_preset"):
                st.session_state.pop("active_viz_preset", None)
                st.rerun()
        config = active_preset
    else:
        config = render_chart_selector(df, key_prefix="viz_studio")

    # Section 3: Plot Rendering & Insights
    _render_chart_output(df, config)


def _render_recommendations_section(df: pd.DataFrame) -> None:
    """Renders the AI/rule-based chart recommendation cards."""
    recommendations = recommend_charts(df, max_recommendations=4)
    if not recommendations:
        return

    with st.expander("⚡ **Smart Chart Recommendations** (Click to Instant Plot)", expanded=True):
        st.caption("Automated suggestions derived from column types, variance, and bivariate correlations:")
        cols = st.columns(len(recommendations))

        for idx, rec in enumerate(recommendations):
            with cols[idx]:
                st.markdown(
                    f"""
                    <div style="border: 1px solid #e0e0e0; border-radius: 8px; padding: 12px; height: 160px; display: flex; flex-direction: column; justify-content: space-between; background-color: #fafafa;">
                        <div>
                            <div style="font-size: 1.1rem; font-weight: 600; margin-bottom: 4px;">{rec['icon']} {rec['chart_type']}</div>
                            <div style="font-size: 0.85rem; font-weight: 500; color: #2b5876; margin-bottom: 6px;">{rec['title']}</div>
                            <div style="font-size: 0.75rem; color: #666; line-height: 1.2;">{rec['reason']}</div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button(f"📊 Plot Preset", key=f"btn_rec_{idx}", use_container_width=True):
                    # Store preset config with validation flag
                    preset_config = dict(rec)
                    preset_config["is_valid"] = True
                    preset_config["error_message"] = None
                    st.session_state["active_viz_preset"] = preset_config
                    st.rerun()


def _render_chart_output(df: pd.DataFrame, config: Dict[str, Any]) -> None:
    """Validates configuration, builds the Plotly figure, and renders export tools."""
    if not config or not config.get("is_valid", False):
        error_msg = config.get("error_message") if config else "Incomplete configuration."
        st.info(f"👉 Select dimensions above to generate your visualization. ({error_msg})")
        return

    chart_type = config.get("chart_type")

    try:
        fig = build_chart_from_config(df, config)

        # Main chart display
        st.plotly_chart(fig, use_container_width=True, key=f"plotly_viz_{chart_type}")

        # Summary Metrics & Chart Details
        _render_chart_summary(df, config)

        # Export Options
        _render_export_options(fig, config)

    except Exception as e:
        st.error(f"⚠️ Unable to render {chart_type}: {str(e)}")


def _render_chart_summary(df: pd.DataFrame, config: Dict[str, Any]) -> None:
    """Renders contextual metrics for the active visualization."""
    chart_type = config.get("chart_type")
    x = config.get("x")
    y = config.get("y")

    st.markdown("##### 🔍 Chart Details & Scope")
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)

    with kpi1:
        st.metric("Chart Type", chart_type)

    with kpi2:
        if chart_type == "Correlation Heatmap":
            cols_count = len(config.get("columns", []))
            st.metric("Features Analyzed", cols_count)
        else:
            primary_col = x or y
            non_null_count = df[primary_col].dropna().shape[0] if primary_col in df.columns else len(df)
            st.metric("Plotted Records", f"{non_null_count:,}")

    with kpi3:
        if y and y in df.columns and pd.api.types.is_numeric_dtype(df[y]):
            mean_val = df[y].mean()
            st.metric(f"Mean ({y})", f"{mean_val:.2f}")
        elif x and x in df.columns and pd.api.types.is_numeric_dtype(df[x]):
            mean_val = df[x].mean()
            st.metric(f"Mean ({x})", f"{mean_val:.2f}")
        else:
            group_label = config.get("color") or "None"
            st.metric("Color Group", group_label)

    with kpi4:
        missing_count = 0
        active_cols = [c for c in [x, y, config.get("color")] if c and c in df.columns]
        if active_cols:
            missing_count = df[active_cols].isna().any(axis=1).sum()
        st.metric("Excluded (NaN) Rows", f"{missing_count:,}")


def _render_export_options(fig: Any, config: Dict[str, Any]) -> None:
    """Renders export controls to download the figure."""
    with st.expander("💾 **Export Visualization**", expanded=False):
        exp_col1, exp_col2 = st.columns(2)

        chart_name = config.get("title", "chart").replace(" ", "_").lower()

        with exp_col1:
            try:
                # Export interactive HTML
                html_buffer = io.StringIO()
                fig.write_html(html_buffer, include_plotlyjs="cdn")
                st.download_button(
                    label="📥 Download Interactive Chart (HTML)",
                    data=html_buffer.getvalue(),
                    file_name=f"{chart_name}.html",
                    mime="text/html",
                    use_container_width=True,
                )
            except Exception as e:
                st.caption(f"HTML export unavailable: {e}")

        with exp_col2:
            st.info("💡 To save as PNG or SVG, hover over the top-right corner of the chart and click the camera icon 📷.")


# Backward compatibility alias
def visualization() -> None:
    """Legacy entry point for the visualization tab."""
    visualization_tab()
