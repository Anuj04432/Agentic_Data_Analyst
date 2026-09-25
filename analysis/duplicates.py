
"""Duplicate detection, inspection, and removal module for Agentic Data Analyst."""

from typing import List, Optional, Tuple, Union
import pandas as pd


def get_duplicate_summary(
    df: Optional[pd.DataFrame],
    subset: Optional[Union[List[str], str]] = None,
) -> dict:
    """
    Summarize duplicate rows in a DataFrame.

    Parameters
    ----------
    df : pd.DataFrame or None
        The input DataFrame to inspect.
    subset : list[str] or str, optional
        Column label or sequence of labels to consider when identifying duplicates.
        If None, all columns are considered.

    Returns
    -------
    dict
        Dictionary containing:
        - "total_rows": int, total number of rows.
        - "duplicate_count": int, count of redundant duplicate rows (keep="first").
        - "duplicate_pct": float, percentage of rows that are duplicates (rounded to 2 decimal places).
        - "has_duplicates": bool, True if at least one duplicate row exists.
        - "duplicate_rows": pd.DataFrame, all duplicate occurrences (keep=False).
    """
    if df is None or df.empty:
        return {
            "total_rows": 0,
            "duplicate_count": 0,
            "duplicate_pct": 0.0,
            "has_duplicates": False,
            "duplicate_rows": pd.DataFrame(),
        }

    # Normalize and validate subset
    subset_cols = None
    if subset is not None:
        if isinstance(subset, str):
            subset_cols = [subset]
        elif isinstance(subset, (list, tuple)):
            subset_cols = list(subset)
            if len(subset_cols) == 0:
                subset_cols = None
        else:
            subset_cols = list(subset)

        if subset_cols is not None:
            missing_cols = [col for col in subset_cols if col not in df.columns]
            if missing_cols:
                raise ValueError(
                    f"Columns not found in DataFrame: {missing_cols}. Available columns: {list(df.columns)}"
                )

    total_rows = len(df)
    duplicate_count = int(df.duplicated(subset=subset_cols, keep="first").sum())
    duplicate_pct = round((duplicate_count / total_rows) * 100, 2) if total_rows > 0 else 0.0
    has_duplicates = duplicate_count > 0

    # Retrieve all rows involved in duplication (keep=False)
    dup_mask = df.duplicated(subset=subset_cols, keep=False)
    duplicate_rows = df[dup_mask].copy()

    # Sort the duplicated rows so matching rows are grouped together
    if not duplicate_rows.empty:
        sort_cols = subset_cols if subset_cols else list(df.columns)
        try:
            duplicate_rows = duplicate_rows.sort_values(by=sort_cols)
        except Exception:
            # Fall back to preserving original order if types are unorderable
            pass

    return {
        "total_rows": total_rows,
        "duplicate_count": duplicate_count,
        "duplicate_pct": duplicate_pct,
        "has_duplicates": has_duplicates,
        "duplicate_rows": duplicate_rows,
    }


def drop_duplicates_clean(
    df: Optional[pd.DataFrame],
    subset: Optional[Union[List[str], str]] = None,
    keep: Union[str, bool] = "first",
) -> Tuple[pd.DataFrame, int]:
    """
    Safely remove duplicate rows from a DataFrame on a copy.

    Parameters
    ----------
    df : pd.DataFrame or None
        The input DataFrame.
    subset : list[str] or str, optional
        Column label or sequence of labels to consider for identifying duplicates.
        If None, all columns are considered.
    keep : {'first', 'last', False, 'none', 'drop_all'}, default 'first'
        Determines which duplicates (if any) to keep:
        - 'first': Keep first occurrence.
        - 'last': Keep last occurrence.
        - False / 'none' / 'drop_all': Drop all duplicate occurrences.

    Returns
    -------
    tuple[pd.DataFrame, int]
        (cleaned_df, removed_count)
        - cleaned_df: pd.DataFrame with duplicates removed and index reset.
        - removed_count: int, number of rows removed.
    """
    if df is None:
        return pd.DataFrame(), 0
    if df.empty:
        return df.copy().reset_index(drop=True), 0

    # Normalize and validate subset
    subset_cols = None
    if subset is not None:
        if isinstance(subset, str):
            subset_cols = [subset]
        elif isinstance(subset, (list, tuple)):
            subset_cols = list(subset)
            if len(subset_cols) == 0:
                subset_cols = None
        else:
            subset_cols = list(subset)

        if subset_cols is not None:
            missing_cols = [col for col in subset_cols if col not in df.columns]
            if missing_cols:
                raise ValueError(
                    f"Columns not found in DataFrame: {missing_cols}. Available columns: {list(df.columns)}"
                )

    # Validate and normalize keep argument
    if isinstance(keep, str):
        keep_normalized = keep.lower().strip()
        if keep_normalized in ("first", "last"):
            keep_val = keep_normalized
        elif keep_normalized in ("false", "none", "drop_all"):
            keep_val = False
        else:
            raise ValueError(
                
                f"Unsupported keep strategy '{keep}'. Supported options: 'first', 'last', False."
            )
    elif keep is False:
        keep_val = False
    else:
        raise ValueError(
            f"Unsupported keep strategy '{keep}'. Supported options: 'first', 'last', False."
        )

    initial_rows = len(df)
    cleaned_df = df.drop_duplicates(subset=subset_cols, keep=keep_val).reset_index(drop=True)
    removed_count = initial_rows - len(cleaned_df)

    return cleaned_df, removed_count
