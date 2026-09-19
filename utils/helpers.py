import pandas as pd


def format_bytes(size_bytes: int | float) -> str:
    if size_bytes is None or size_bytes<=0:
        return "0 B"
    for unit in ["B","KB","MB","GB","TB"]:
        if abs(size_bytes) < 1024.0:
            return f"{size_bytes:.2f} {unit}" if unit != "B" else f"{int(size_bytes)} B"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def format_number(val: int | float | None, precision: int = 2) -> str:
    if val is None or pd.isna(val):
        return "N/A"
    if isinstance(val, (int,)):
        return f"{val:,}"
    return f"{val:,.{precision}f}"


def format_percentage(val: float |None, precision: int = 1) -> str:
    if val is None or pd.isna(val):
        return "N/A"
    return f"{val:.{precision}f}%"


def get_column_types(df: pd.DataFrame) -> dict[str, list[str]]:
    if df is None or df.empty:
        return {"num_cols" : [],
                "cat_cols" : [],
                "date_cols" : [],
                "boolean" : []}
    return {
        "num_cols": df.select_dtypes(include="number").columns.tolist(),
        "cat_cols":df.select_dtypes(include=["object","category"]).columns.tolist(),
        "datetime":df.select_dtypes(include=["datetime","datetimetz"]).columns.tolist(),
        "boolean":df.select_dtypes(include="bool").columns.tolist(),
        "all":df.columns.tolist(),
    }

    