"""
Modular Streamlit UI components for Agentic Data Analyst.
"""

from components.dataset_summary import (
    extract_summary_metrics,
    render_dataset_summary,
)
from components.data_preview import (
    filter_preview_data,
    paginate_data,
    render_data_preview,
)
from components.column_selector import (
    classify_columns,
    filter_columns_by_type,
    render_column_select,
    render_column_multiselect,
    render_type_aware_selector,
)

__all__ = [
    "extract_summary_metrics",
    "render_dataset_summary",
    "filter_preview_data",
    "paginate_data",
    "render_data_preview",
    "classify_columns",
    "filter_columns_by_type",
    "render_column_select",
    "render_column_multiselect",
    "render_type_aware_selector",
]

