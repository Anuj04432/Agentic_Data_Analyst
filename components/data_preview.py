import math
from typing import Any, Dict, List, Optional, Union
import pandas as pd
import streamlit as st


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


def render_data_preview(
    df: Optional[pd.DataFrame],
    default_page_size: int = 25,
    key_prefix: str = "preview",
) -> pd.DataFrame:
    """
    Renders an interactive data preview component with full-text search,
    column selection, pagination controls, and CSV export.

    Args:
        df: DataFrame to display.
        default_page_size: Default rows per page (10, 25, 50, 100).
        key_prefix: Unique widget key prefix to avoid Streamlit collisions.

    Returns:
        The currently displayed/sliced DataFrame.
    """
    if df is None or df.empty:
        st.info("ℹ️ No dataset loaded to display preview.")
        return pd.DataFrame()

    page_state_key = f"{key_prefix}_current_page"
    if page_state_key not in st.session_state:
        st.session_state[page_state_key] = 1

    # 1. Top Controls Bar
    ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([3, 4, 2])

    with ctrl_col1:
        search_query = st.text_input(
            "🔍 Search rows",
            placeholder="Type keywords...",
            key=f"{key_prefix}_search",
            help="Case-insensitive literal search across all displayed columns",
        )

    with ctrl_col2:
        all_cols = list(df.columns)
        selected_cols = st.multiselect(
            "📐 Columns to display",
            options=all_cols,
            default=all_cols,
            key=f"{key_prefix}_cols",
            help="Select columns to show in the preview table",
        )

    with ctrl_col3:
        page_size_options = [10, 25, 50, 100, "All"]
        default_index = (
            page_size_options.index(default_page_size)
            if default_page_size in page_size_options
            else 1
        )
        page_size = st.selectbox(
            "📄 Rows per page",
            options=page_size_options,
            index=default_index,
            key=f"{key_prefix}_page_size",
        )

    # 2. Filter & Paginate
    filtered_df = filter_preview_data(
        df=df,
        search_term=search_query,
        selected_columns=selected_cols,
    )

    current_page = st.session_state[page_state_key]
    sliced_df, page_info = paginate_data(
        df=filtered_df,
        page=current_page,
        page_size=page_size,
    )

    # Sync state if clamped by pagination logic
    st.session_state[page_state_key] = page_info["page"]

    # 3. Status Bar
    total_unfiltered = len(df)
    total_matching = page_info["total_rows"]

    if total_matching == 0:
        st.warning(f"⚠️ No records match the search query: '{search_query}'")
        return pd.DataFrame(columns=filtered_df.columns)

    if search_query and search_query.strip():
        st.caption(
            f"Showing rows **{page_info['display_start']}–{page_info['display_end']}** "
            f"of **{total_matching:,}** matching (filtered from {total_unfiltered:,} total) "
            f"• **{len(sliced_df.columns)}** columns displayed"
        )
    else:
        st.caption(
            f"Showing rows **{page_info['display_start']}–{page_info['display_end']}** "
            f"of **{total_matching:,}** total "
            f"• **{len(sliced_df.columns)}** of {len(all_cols)} columns displayed"
        )

    # 4. Interactive Table
    st.dataframe(
        sliced_df,
        use_container_width=True,
        hide_index=False,
    )

    # 5. Footer: Pagination Navigation & Download
    foot_col1, foot_col2, foot_col3, foot_col4 = st.columns([2, 3, 2, 3])

    with foot_col1:
        if page_info["total_pages"] > 1:
            if st.button("◀ Previous", key=f"{key_prefix}_prev_btn", disabled=not page_info["has_prev"]):
                st.session_state[page_state_key] = max(1, page_info["page"] - 1)
                st.rerun()

    with foot_col2:
        if page_info["total_pages"] > 1:
            st.markdown(
                f"<div style='text-align: center; padding-top: 6px; font-weight: 500;'>"
                f"Page {page_info['page']} of {page_info['total_pages']}</div>",
                unsafe_allow_html=True,
            )

    with foot_col3:
        if page_info["total_pages"] > 1:
            if st.button("Next ▶", key=f"{key_prefix}_next_btn", disabled=not page_info["has_next"]):
                st.session_state[page_state_key] = min(page_info["total_pages"], page_info["page"] + 1)
                st.rerun()

    with foot_col4:
        csv_data = sliced_df.to_csv(index=False)
        st.download_button(
            label="📥 Download View (CSV)",
            data=csv_data,
            file_name="data_preview.csv",
            mime="text/csv",
            key=f"{key_prefix}_download_btn",
        )

    return sliced_df