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


def get_column_summary(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return "Dataset is empty so use a valid dataset"

    summary = []
    total_rows = len(df)

    for col in df.columns:
        series = df[col]
        no_null = int(series.notna().sum())
        missing_values =int(series.isnull().sum())
        missing_percent = round((missing_values/ total_rows *100),2) if total_rows > 0 else 0.0
        unique_count = int(series.nunique(dropna=True))

        sample_vals = series.dropna().unique()[:3]
        sample_str = ", ".join(str(val) for val in sample_vals)
        if len(sample_str) > 50 :
            sample_str = sample_str[:47] + "..."

        summary.append({
            "columns": col,
            "Data Type": str(series.dtype),
            "Non-Null values": no_null,
            "Null values": missing_values,
            "Missing percent": missing_percent,
            "Unique values": unique_count,
            "Sample values":sample_str if sample_str else "N/A"
        })

    return pd.DataFrame(summary)


    