import pandas as pd
import numpy as np

def get_missing_summary(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()

    total_rows = len(df)

    records = []

    for col in df.columns:
        missing = df[col].isna().sum()
        missing_percent = round((missing/total_rows) *100,2)
        data_type = str(df[col].dtype)
        has_missing = missing > 0

        records.append({
            "Column":col,
            "Data Type": data_type,
            "Total Rows":total_rows,
            "Missing Count": int(missing),
            "Missing %": missing_percent,
            "Has Missing": has_missing
        })

    res_df = pd.DataFrame(records)
    if not res_df.empty:
        res_df = res_df.sort_values(by="Missing %", ascending=False).reset_index(drop=True)
    return res_df


def get_missingness_overview(df: pd.DataFrame) -> dict:
    if df is None or df.empty:
        return {
            "total_missing_cells": 0,
            "total_cells": 0,
            "overall_missing_pct": 0.0,
            "columns_with_missing_count": 0,
            "columns_with_missing": []
        }

    total_rows = len(df)
    total_cols = len(df.columns)
    total_cells = total_rows * total_cols
    total_missing_cells = int(df.isna().sum().sum())
    overall_missing_pct = round((total_missing_cells / total_cells) * 100, 2) if total_cells > 0 else 0.0

    missing_series = df.isna().sum()
    columns_with_missing = missing_series[missing_series > 0].index.tolist()

    return {
        "total_missing_cells": total_missing_cells,
        "total_cells": total_cells,
        "overall_missing_pct": overall_missing_pct,
        "columns_with_missing_count": len(columns_with_missing),
        "columns_with_missing": columns_with_missing
    }


def impute_missing_values(df: pd.DataFrame, strategy: str = "auto", custom_values: dict = None) -> pd.DataFrame:
    if df is None:
        return pd.DataFrame()
    if df.empty:
        return df.copy()

    df_clean = df.copy()

    if custom_values is not None:
        return df_clean.fillna(value=custom_values)

    strategy_normalized = strategy.lower().strip()

    if strategy_normalized == "drop_rows":
        return df_clean.dropna().reset_index(drop=True)

    if strategy_normalized == "drop_cols":
        return df_clean.dropna(axis=1)

    if strategy_normalized == "mean":
        num_cols = df_clean.select_dtypes(include="number").columns
        for col in num_cols:
            if df_clean[col].notna().any():
                df_clean[col] = df_clean[col].fillna(df_clean[col].mean())
        return df_clean

    if strategy_normalized == "median":
        num_cols = df_clean.select_dtypes(include="number").columns
        for col in num_cols:
            if df_clean[col].notna().any():
                df_clean[col] = df_clean[col].fillna(df_clean[col].median())
        return df_clean

    if strategy_normalized == "mode":
        for col in df_clean.columns:
            mode_vals = df_clean[col].mode(dropna=True)
            if not mode_vals.empty:
                df_clean[col] = df_clean[col].fillna(mode_vals.iloc[0])
        return df_clean

    
    if strategy_normalized == "auto":
        num_cols = df_clean.select_dtypes(include="number").columns
        non_num_cols = [c for c in df_clean.columns if c not in num_cols]

        for col in num_cols:
            if df_clean[col].notna().any():
                df_clean[col] = df_clean[col].fillna(df_clean[col].median())

        for col in non_num_cols:
            mode_vals = df_clean[col].mode(dropna=True)
            if not mode_vals.empty:
                df_clean[col] = df_clean[col].fillna(mode_vals.iloc[0])

        return df_clean

    raise ValueError(
        f"Unsupported strategy '{strategy}'. Supported strategies: 'auto', 'mean', 'median', 'mode', 'drop_rows', 'drop_cols'."
    )
    