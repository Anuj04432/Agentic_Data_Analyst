import math
from typing import Any, Dict, List, Optional, Union
import pandas as pd


def filter_preview_data(
    df: Optional[pd.DataFrame],
    search_term: Optional[str] = None,
    selected_columns: Optional[List[str]] = None,
) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()

    cols_to_keep = []
    if selected_columns is None or selected_columns == []:
        cols_to_keep = list(df.columns)

    if selected_columns:
        cols_to_keep = [col for col in selected_columns if col in df.columns]

    if not cols_to_keep:
        cols_to_keep = list(df.columns)

    filtered_df = df[cols_to_keep]

    if search_term is None or search_term.strip() == "":
        return filtered_df

    clean_term = search_term.strip().lower()

    mask = pd.Series(False, index=filtered_df.index)

    for col in cols_to_keep:
        col_mask = (
            filtered_df[col]
            .astype(str)
            .str.contains(clean_term, case=False, na=False, regex=False)
        )
        mask = mask | col_mask

    return filtered_df[mask]


def paginate_data(
    df: Optional[pd.DataFrame],
    page: int = 1,
    page_size: Union[int, str] = 25,
) -> tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Paginates a DataFrame based on requested page number and page size.

    Args:
        df: Source DataFrame to paginate.
        page: Current 1-based page number.
        page_size: Number of rows per page or "All" to return full data.

    Returns:
        Tuple of (sliced_df, pagination_info_dict).
    """
    default_empty_metadata = {
        "total_rows": 0,
        "total_pages": 1,
        "page": 1,
        "page_size": page_size,
        "display_start": 0,
        "display_end": 0,
        "has_prev": False,
        "has_next": False,
    }

    if df is None or df.empty:
        return (pd.DataFrame(), default_empty_metadata)

    total_rows = len(df)

    # 1. Fast-path: "All" selected
    if isinstance(page_size, str) and page_size.strip().lower() == "all":
        return (
            df,
            {
                "total_rows": total_rows,
                "total_pages": 1,
                "page": 1,
                "page_size": "All",
                "display_start": 1 if total_rows > 0 else 0,
                "display_end": total_rows,
                "has_prev": False,
                "has_next": False,
            },
        )

    # 2. Sanitize page_size
    try:
        size = int(page_size)
        if size <= 0:
            size = 25
    except (ValueError, TypeError):
        size = 25

    # 3. Calculate total pages
    total_pages = max(1, math.ceil(total_rows / size))

    # 4. Clamp current page bounds
    current_page = max(1, min(page, total_pages))

    # 5. Positional slicing math (0-indexed)
    start_idx = (current_page - 1) * size
    end_idx = min(start_idx + size, total_rows)

    sliced_df = df.iloc[start_idx:end_idx]

    # 6. Build UI metadata
    pagination_info = {
        "total_rows": total_rows,
        "total_pages": total_pages,
        "page": current_page,
        "page_size": size,
        "display_start": start_idx + 1 if total_rows > 0 else 0,
        "display_end": end_idx,
        "has_prev": current_page > 1,
        "has_next": current_page < total_pages,
    }

    return (sliced_df, pagination_info)
    