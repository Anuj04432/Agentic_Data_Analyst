"""
Visual status cards and badges for Agentic Data Analyst.
Renders styled cards for Data Health Grade, Actionable Warnings,
Distribution shapes, and Correlation strength.
"""

from typing import Any, Dict, List, Optional
import html
import streamlit as st


def get_health_grade_color(grade: str) -> Dict[str, str]:
    """
    Returns color palette, border, and description for a health grade letter.

    Args:
        grade: Letter grade ('A', 'B', 'C', 'D', 'F').

    Returns:
        Dict with 'color', 'background', 'border', and 'label'.
    """
    grade_clean = str(grade).strip().upper()

    palettes: Dict[str, Dict[str, str]] = {
        "A": {
            "color": "#10b981",
            "background": "#ecfdf5",
            "border": "#a7f3d0",
            "label": "Excellent",
        },
        "B": {
            "color": "#3b82f6",
            "background": "#eff6ff",
            "border": "#bfdbfe",
            "label": "Good",
        },
        "C": {
            "color": "#f59e0b",
            "background": "#fffbeb",
            "border": "#fde68a",
            "label": "Fair",
        },
        "D": {
            "color": "#f97316",
            "background": "#fff7ed",
            "border": "#fed7aa",
            "label": "Poor",
        },
        "F": {
            "color": "#ef4444",
            "background": "#fef2f2",
            "border": "#fecaca",
            "label": "Critical",
        },
    }

    return palettes.get(
        grade_clean,
        {
            "color": "#6b7280",
            "background": "#f3f4f6",
            "border": "#e5e7eb",
            "label": "Unknown",
        },
    )


def get_distribution_badge_info(skew_interp: str) -> Dict[str, str]:
    """
    Translates distribution skewness interpretation into badge styling metadata.

    Args:
        skew_interp: Interpretation string from get_distribution_stats.

    Returns:
        Dict with 'label', 'color', 'background', 'border', and 'icon'.
    """
    interp_lower = str(skew_interp).lower()

    if "symmetrical" in interp_lower or "normal" in interp_lower:
        return {
            "label": "Symmetrical",
            "color": "#10b981",
            "background": "#ecfdf5",
            "border": "#a7f3d0",
            "icon": "⚖️",
        }
    elif "highly skewed (right)" in interp_lower:
        return {
            "label": "Highly Right-Skewed",
            "color": "#ef4444",
            "background": "#fef2f2",
            "border": "#fecaca",
            "icon": "📈",
        }
    elif "skewed (right)" in interp_lower or "right" in interp_lower:
        return {
            "label": "Right-Skewed",
            "color": "#f59e0b",
            "background": "#fffbeb",
            "border": "#fde68a",
            "icon": "📈",
        }
    elif "highly skewed (left)" in interp_lower:
        return {
            "label": "Highly Left-Skewed",
            "color": "#ef4444",
            "background": "#fef2f2",
            "border": "#fecaca",
            "icon": "📉",
        }
    elif "skewed (left)" in interp_lower or "left" in interp_lower:
        return {
            "label": "Left-Skewed",
            "color": "#f59e0b",
            "background": "#fffbeb",
            "border": "#fde68a",
            "icon": "📉",
        }
    else:
        return {
            "label": skew_interp if skew_interp else "Unknown",
            "color": "#6b7280",
            "background": "#f3f4f6",
            "border": "#e5e7eb",
            "icon": "📊",
        }


def get_correlation_badge_info(corr: float) -> Dict[str, str]:
    """
    Translates correlation coefficient into direction, strength, and badge metadata.

    Args:
        corr: Pearson / Spearman correlation coefficient (-1.0 to 1.0).

    Returns:
        Dict with 'label', 'color', 'background', 'border', and 'icon'.
    """
    try:
        val = float(corr)
    except (ValueError, TypeError):
        val = 0.0

    if val >= 0.7:
        return {
            "label": f"Strong Positive ({val:+.2f})",
            "color": "#10b981",
            "background": "#ecfdf5",
            "border": "#a7f3d0",
            "icon": "🟢",
        }
    elif val >= 0.3:
        return {
            "label": f"Moderate Positive ({val:+.2f})",
            "color": "#3b82f6",
            "background": "#eff6ff",
            "border": "#bfdbfe",
            "icon": "🔵",
        }
    elif val > -0.3:
        return {
            "label": f"Weak / Negligible ({val:+.2f})",
            "color": "#6b7280",
            "background": "#f3f4f6",
            "border": "#e5e7eb",
            "icon": "⚪",
        }
    elif val > -0.7:
        return {
            "label": f"Moderate Negative ({val:+.2f})",
            "color": "#f59e0b",
            "background": "#fffbeb",
            "border": "#fde68a",
            "icon": "🟠",
        }
    else:
        return {
            "label": f"Strong Negative ({val:+.2f})",
            "color": "#ef4444",
            "background": "#fef2f2",
            "border": "#fecaca",
            "icon": "🔴",
        }


# ==============================================================================
# STREAMLIT UI RENDERING FUNCTIONS
# ==============================================================================


def render_health_grade_badge(
    grade: str,
    score: Optional[float] = None,
    size: str = "medium",
) -> str:
    """
    Generates and renders an inline HTML badge for a dataset health grade.

    Args:
        grade: Letter grade ('A' to 'F').
        score: Optional numeric health score out of 100.
        size: 'small', 'medium', or 'large'.

    Returns:
        Rendered HTML markup string.
    """
    palette = get_health_grade_color(grade)
    grade_clean = html.escape(str(grade).strip().upper())
    label_text = f"Grade {grade_clean}"
    if score is not None:
        label_text += f" ({score:.1f}/100)"

    font_sizes = {"small": "12px", "medium": "14px", "large": "20px"}
    paddings = {"small": "2px 8px", "medium": "4px 12px", "large": "8px 18px"}

    font_size = font_sizes.get(size, "14px")
    padding = paddings.get(size, "4px 12px")

    badge_html = (
        f"<span style='display: inline-flex; align-items: center; justify-content: center; "
        f"background-color: {palette['background']}; color: {palette['color']}; "
        f"border: 1px solid {palette['border']}; border-radius: 9999px; "
        f"padding: {padding}; font-size: {font_size}; font-weight: 700; "
        f"letter-spacing: 0.025em; text-transform: uppercase;'>"
        f"{label_text} • {palette['label']}</span>"
    )

    st.markdown(badge_html, unsafe_allow_html=True)
    return badge_html


def render_health_score_card(
    health_data: Optional[Dict[str, Any]],
    border: bool = True,
) -> None:
    """
    Renders the Hero Card for dataset quality health score, grade,
    deductions breakdown, and summary.

    Args:
        health_data: Dictionary returned by calculate_health_score() or
                     audit.get('health').
        border: Whether to wrap the card in a bordered container.
    """
    if not health_data:
        st.info("ℹ️ No health diagnostic data available.")
        return

    score = float(health_data.get("health_score", 0.0))
    grade = str(health_data.get("grade", "N/A"))
    summary = str(health_data.get("summary", "No summary available."))
    deductions = health_data.get("deductions", {})

    palette = get_health_grade_color(grade)

    def _draw_content():
        head_col, score_col = st.columns([3, 1])

        with head_col:
            st.markdown(f"### 🛡️ Dataset Health Audit")
            st.caption(summary)

        with score_col:
            st.markdown(
                f"<div style='text-align: right;'>"
                f"<div style='font-size: 32px; font-weight: 800; color: {palette['color']}; "
                f"line-height: 1.1;'>Grade {grade}</div>"
                f"<div style='font-size: 14px; font-weight: 600; color: #6b7280;'>"
                f"{score:.1f} / 100 ({palette['label']})</div>"
                f"</div>",
                unsafe_allow_html=True,
            )

        # Progress bar representing 0-100 score
        st.progress(min(1.0, max(0.0, score / 100.0)))

        # Deductions breakdown pills
        if isinstance(deductions, dict):
            d_cols = st.columns(4)
            d_items = [
                ("❓ Missing", deductions.get("missing", 0.0)),
                ("👥 Duplicates", deductions.get("duplicates", 0.0)),
                ("🚨 Outliers", deductions.get("outliers", 0.0)),
                ("⚠️ Constant Cols", deductions.get("constant_cols", 0.0)),
            ]
            for col_widget, (lbl, ded_val) in zip(d_cols, d_items):
                with col_widget:
                    val_float = float(ded_val)
                    if val_float > 0:
                        st.caption(f"{lbl}: **-{val_float:.1f} pts**")
                    else:
                        st.caption(f"{lbl}: **0 pts (Clean)**")

    if border:
        with st.container(border=True):
            _draw_content()
    else:
        _draw_content()


def render_actionable_warnings(
    warnings: Optional[List[str]],
    expanded: bool = False,
) -> None:
    """
    Renders diagnostic alerts and actionable quality recommendations.

    Args:
        warnings: List of warning strings from generate_dataset_audit().
        expanded: Whether the warning expander is expanded by default.
    """
    if warnings is None or len(warnings) == 0:
        st.success("✅ **Clean Dataset**: No critical data hygiene issues or high-risk warnings detected.")
        return

    # Check if the only warning is that dataset is empty
    if len(warnings) == 1 and "empty" in warnings[0].lower():
        st.info(f"ℹ️ {warnings[0]}")
        return

    warn_count = len(warnings)
    title = f"⚠️ Diagnostic Alerts & Recommendations ({warn_count} issue{'s' if warn_count > 1 else ''} found)"

    with st.expander(title, expanded=expanded):
        for warning in warnings:
            warn_clean = html.escape(str(warning))
            # Choose contextual icon
            if "missing" in warn_clean.lower():
                icon = "❓"
            elif "duplicate" in warn_clean.lower():
                icon = "👥"
            elif "outlier" in warn_clean.lower():
                icon = "🚨"
            elif "multicollinearity" in warn_clean.lower() or "correlation" in warn_clean.lower():
                icon = "🔗"
            elif "constant" in warn_clean.lower() or "zero variance" in warn_clean.lower():
                icon = "⚠️"
            else:
                icon = "📌"

            st.markdown(
                f"<div style='padding: 6px 10px; margin-bottom: 6px; border-radius: 6px; "
                f"background-color: #fffbeb; border-left: 4px solid #f59e0b; font-size: 14px;'>"
                f"{icon} {warn_clean}"
                f"</div>",
                unsafe_allow_html=True,
            )


def render_distribution_badge(skew_interp: str) -> str:
    """
    Renders an inline badge showing distribution shape.

    Args:
        skew_interp: Skewness interpretation string.

    Returns:
        Rendered HTML markup string.
    """
    info = get_distribution_badge_info(skew_interp)
    badge_html = (
        f"<span style='display: inline-flex; align-items: center; gap: 4px; "
        f"background-color: {info['background']}; color: {info['color']}; "
        f"border: 1px solid {info['border']}; border-radius: 9999px; "
        f"padding: 2px 10px; font-size: 13px; font-weight: 600;'>"
        f"{info['icon']} {html.escape(info['label'])}</span>"
    )
    st.markdown(badge_html, unsafe_allow_html=True)
    return badge_html


def render_correlation_badge(corr_val: float) -> str:
    """
    Renders an inline badge showing correlation direction and strength.

    Args:
        corr_val: Correlation coefficient value.

    Returns:
        Rendered HTML markup string.
    """
    info = get_correlation_badge_info(corr_val)
    badge_html = (
        f"<span style='display: inline-flex; align-items: center; gap: 4px; "
        f"background-color: {info['background']}; color: {info['color']}; "
        f"border: 1px solid {info['border']}; border-radius: 9999px; "
        f"padding: 2px 10px; font-size: 13px; font-weight: 600;'>"
        f"{info['icon']} {html.escape(info['label'])}</span>"
    )
    st.markdown(badge_html, unsafe_allow_html=True)
    return badge_html
