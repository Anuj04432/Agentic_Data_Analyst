"""
Smart column selector components for Agentic Data Analyst.
Provides type-aware column filtering and Streamlit dropdown/multiselect widgets.
"""

from typing import Any, Dict, List, Optional, Union
import pandas as pd
import streamlit as st


def classify_columns(df: Optional[pd.DataFrame]) -> Dict[str, List[str]]:
    """
    Classifies DataFrame columns by their analytical data types.

    Args:
        df: Input DataFrame to classify.

    Returns:
        Dict mapping column type keys ("all", "numeric", "categorical", "datetime", "boolean")
        to lists of column names.
    """
    default_empty: Dict[str, List[str]] = {
        "all": [],
        "numeric": [],
        "categorical": [],
        "datetime": [],
        "boolean": [],
    }

    if df is None or df.empty:
        return default_empty

    all_cols = list(df.columns)
    num_cols = df.select_dtypes(include=["number"]).columns.tolist()
    cat_cols = df.select_dtypes(include=["object", "category", "string"]).columns.tolist()
    date_cols = df.select_dtypes(include=["datetime", "datetimetz", "timedelta"]).columns.tolist()
    bool_cols = df.select_dtypes(include=["bool", "boolean"]).columns.tolist()

    return {
        "all": all_cols,
        "numeric": num_cols,
        "categorical": cat_cols,
        "datetime": date_cols,
        "boolean": bool_cols,
    }


def filter_columns_by_type(
    df: Optional[pd.DataFrame],
    col_type: str = "all",
    exclude: Optional[List[str]] = None,
) -> List[str]:
    """
    Filters DataFrame columns by analytical type, optionally excluding specific columns.

    Args:
        df: Input DataFrame.
        col_type: Type filter ("all", "numeric", "categorical", "datetime", "boolean").
        exclude: Optional list of column names to omit from results.

    Returns:
        List of matching column names preserving original column order.
    """
    if df is None or df.empty:
        return []

    classes = classify_columns(df)
    normalized_type = str(col_type).strip().lower()

    if normalized_type in ("numeric", "num", "numbers", "numerical"):
        candidates = classes["numeric"]
    elif normalized_type in ("categorical", "cat", "categories", "string", "text"):
        candidates = classes["categorical"]
    elif normalized_type in ("datetime", "date", "time", "temporal"):
        candidates = classes["datetime"]
    elif normalized_type in ("boolean", "bool"):
        candidates = classes["boolean"]
    elif normalized_type in ("all", "*"):
        candidates = classes["all"]
    else:
        candidates = classes["all"]

    if exclude:
        exclude_set = set(exclude)
        return [c for c in candidates if c not in exclude_set]

    return list(candidates)


def render_column_select(
    df: Optional[pd.DataFrame],
    label: str = "Select Column",
    column_type: str = "all",
    default: Optional[str] = None,
    allow_none: bool = False,
    none_label: str = "-- Select a column --",
    exclude_columns: Optional[List[str]] = None,
    key: Optional[str] = None,
    help_text: Optional[str] = None,
    disabled: bool = False,
) -> Optional[str]:
    """
    Renders a single-column selectbox filtered by analytical data type.

    Args:
        df: Source DataFrame.
        label: Label displayed above selectbox.
        column_type: Analytical type filter ("all", "numeric", "categorical", etc.).
        default: Preferred default column name.
        allow_none: If True, prepends a null placeholder option.
        none_label: Text for the null placeholder option.
        exclude_columns: Columns to exclude from selection.
        key: Streamlit widget key.
        help_text: Tooltip help text.
        disabled: Whether the selectbox is disabled.

    Returns:
        Selected column name, or None if none chosen or dataset empty.
    """
    if df is None or df.empty:
        st.info("ℹ️ No dataset available for column selection.")
        return None

    candidates = filter_columns_by_type(df, col_type=column_type, exclude=exclude_columns)

    if not candidates:
        st.warning(f"⚠️ No '{column_type}' columns available in the dataset.")
        return None

    options = [none_label] + candidates if allow_none else candidates

    default_index = 0
    if default is not None and default in options:
        default_index = options.index(default)
    elif allow_none and default is None:
        default_index = 0

    selected = st.selectbox(
        label=label,
        options=options,
        index=default_index,
        key=key,
        help=help_text,
        disabled=disabled,
    )

    if allow_none and selected == none_label:
        return None

    return selected


def render_column_multiselect(
    df: Optional[pd.DataFrame],
    label: str = "Select Columns",
    column_type: str = "all",
    default_all: bool = False,
    default_columns: Optional[List[str]] = None,
    exclude_columns: Optional[List[str]] = None,
    key: Optional[str] = None,
    help_text: Optional[str] = None,
    disabled: bool = False,
    max_selections: Optional[int] = None,
) -> List[str]:
    """
    Renders a multi-column selector filtered by analytical data type.

    Args:
        df: Source DataFrame.
        label: Label displayed above multiselect.
        column_type: Analytical type filter ("all", "numeric", "categorical", etc.).
        default_all: If True, selects all matching columns by default.
        default_columns: Specific subset of columns to pre-select.
        exclude_columns: Columns to exclude from selection options.
        key: Streamlit widget key.
        help_text: Tooltip help text.
        disabled: Whether the widget is disabled.
        max_selections: Maximum allowed selected items.

    Returns:
        List of selected column names.
    """
    if df is None or df.empty:
        st.info("ℹ️ No dataset available for column selection.")
        return []

    candidates = filter_columns_by_type(df, col_type=column_type, exclude=exclude_columns)

    if not candidates:
        st.warning(f"⚠️ No '{column_type}' columns available in the dataset.")
        return []

    sanitized_defaults: List[str] = []
    if default_all:
        sanitized_defaults = list(candidates)
    elif default_columns is not None:
        sanitized_defaults = [c for c in default_columns if c in candidates]

    if max_selections is not None and len(sanitized_defaults) > max_selections:
        sanitized_defaults = sanitized_defaults[:max_selections]

    selected = st.multiselect(
        label=label,
        options=candidates,
        default=sanitized_defaults,
        key=key,
        help=help_text,
        disabled=disabled,
        max_selections=max_selections,
    )

    return selected


def render_type_aware_selector(
    df: Optional[pd.DataFrame],
    label: str = "Select Column",
    default_type: str = "all",
    allow_none: bool = False,
    none_label: str = "-- Select a column --",
    exclude_columns: Optional[List[str]] = None,
    key_prefix: str = "type_aware_col",
    multiselect: bool = False,
    default_all: bool = False,
    default_columns: Optional[List[str]] = None,
    help_text: Optional[str] = None,
) -> Union[Optional[str], List[str]]:
    """
    Renders an interactive data-type filter bar (All / Numeric / Categorical / Datetime / Boolean)
    paired with a column selector.

    Args:
        df: Source DataFrame.
        label: Label displayed above selector.
        default_type: Initial filter type ("all", "numeric", "categorical", etc.).
        allow_none: If True and multiselect is False, allows selecting None.
        none_label: Text for null placeholder in single-select mode.
        exclude_columns: Columns to exclude from selection options.
        key_prefix: Unique widget key prefix.
        multiselect: If True, renders multiselect widget; otherwise single selectbox.
        default_all: For multiselect, whether to select all matching by default.
        default_columns: Specific subset of columns to pre-select.
        help_text: Tooltip help text.

    Returns:
        Selected column name (str or None) if multiselect=False, or list of column names if True.
    """
    if df is None or df.empty:
        st.info("ℹ️ No dataset available for column selection.")
        return [] if multiselect else None

    type_options = ["All", "Numeric", "Categorical", "Datetime", "Boolean"]
    type_map = {
        "All": "all",
        "Numeric": "numeric",
        "Categorical": "categorical",
        "Datetime": "datetime",
        "Boolean": "boolean",
    }

    norm_default = default_type.strip().capitalize()
    default_idx = type_options.index(norm_default) if norm_default in type_options else 0

    # Type switcher UI
    if hasattr(st, "pills"):
        selected_category = st.pills(
            "Filter column type",
            options=type_options,
            default=type_options[default_idx],
            key=f"{key_prefix}_filter_pills",
            label_visibility="collapsed",
        )
    elif hasattr(st, "segmented_control"):
        selected_category = st.segmented_control(
            "Filter column type",
            options=type_options,
            default=type_options[default_idx],
            key=f"{key_prefix}_filter_seg",
            label_visibility="collapsed",
        )
    else:
        selected_category = st.radio(
            "Filter column type",
            options=type_options,
            index=default_idx,
            horizontal=True,
            key=f"{key_prefix}_filter_radio",
            label_visibility="collapsed",
        )

    chosen_type = type_map.get(str(selected_category), "all")

    if multiselect:
        return render_column_multiselect(
            df=df,
            label=label,
            column_type=chosen_type,
            default_all=default_all,
            default_columns=default_columns,
            exclude_columns=exclude_columns,
            key=f"{key_prefix}_multi_select_{chosen_type}",
            help_text=help_text,
        )
    else:
        return render_column_select(
            df=df,
            label=label,
            column_type=chosen_type,
            allow_none=allow_none,
            none_label=none_label,
            exclude_columns=exclude_columns,
            key=f"{key_prefix}_single_select_{chosen_type}",
            help_text=help_text,
        )
