"""Analysis engine package for Agentic Data Analyst."""

from analysis.statistics import (
    get_numeric_summary,
    get_categorical_summary,
    get_distribution_stats,
)
from analysis.missing_values import (
    get_missing_summary,
    get_missingness_overview,
    impute_missing_values,
)
from analysis.duplicates import (
    get_duplicate_summary,
    drop_duplicates_clean,
)
from analysis.correlations import (
    calculate_correlation_matrix,
    get_top_correlations,
    get_target_correlations,
    get_correlation_overview,
)

__all__ = [
    "get_numeric_summary",
    "get_categorical_summary",
    "get_distribution_stats",
    "get_missing_summary",
    "get_missingness_overview",
    "impute_missing_values",
    "get_duplicate_summary",
    "drop_duplicates_clean",
    "calculate_correlation_matrix",
    "get_top_correlations",
    "get_target_correlations",
    "get_correlation_overview",
]

