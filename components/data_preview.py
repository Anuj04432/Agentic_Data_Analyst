import pandas as pd
from typing import Optional,List


def filter_preview_data(
        df:Optional[pd.DataFrame],
        search_term: Optional[str] = None,
        selected_columns: Optional[List[str]] = None
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

    mask = pd.Series(False, index = filtered_df.index)

    for col in cols_to_keep:
        col_mask = (filtered_df[col].astype(str).str.contains(clean_term,case=False, na=False, regex=False))
        mask = mask | col_mask

    return filtered_df[mask]

# def paginate_data()





    