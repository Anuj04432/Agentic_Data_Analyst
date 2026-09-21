import pandas as pd
import re


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
                "datetime" : [],
                "boolean" : [],
                "all": []}
    return {
        "num_cols": df.select_dtypes(include="number").columns.tolist(),
        "cat_cols":df.select_dtypes(include=["object","category"]).columns.tolist(),
        "datetime":df.select_dtypes(include=["datetime","datetimetz"]).columns.tolist(),
        "boolean":df.select_dtypes(include="bool").columns.tolist(),
        "all":df.columns.tolist(),
    }


def get_column_summary(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()

    summary = []
    total_rows = len(df)

    for col in df.columns:
        series = df[col]
        no_null = int(series.notna().sum())
        missing_values =int(series.isnull().sum())
        missing_percent = round((missing_values/ total_rows *100),2) if total_rows > 0 else 0.0
        unique_count = int(series.nunique(dropna=True))

        sample_vals = series.dropna().unique()[:3]
        sample_str =truncate_string(", ".join(str(val) for val in sample_vals),max_len=50)
        

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


def clean_column_name(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return df

    df_copy = df.copy()

    cleaned_cols = []
    for i, col in enumerate(df_copy.columns):
        name = str(col).strip().lower()

        name = re.sub(r"[^\w\s]","_",name)
        name = re.sub(r"\s+","_",name)
        name = re.sub(r"_+","_",name).strip("_")

        cleaned_cols.append(name if name else f"col_{i+1}")

    df_copy.columns = cleaned_cols

    return df_copy


def truncate_string(val: object, max_len: int =50) -> str:
    if val is None or pd.isna(val):
        return "N/A"

    val = str(val)
    val = val.strip()
    if len(val) <= max_len:
        return val
    if max_len <= 3:
        return val[:max_len]
    return val[:max_len-3]+"..."


def detect_outliers_iqr(series: pd.Series) -> tuple:
    if series is None or series.empty or series.isna().all() or not pd.api.types.is_numeric_dtype(series):
        return (0,0.0)

    clean_series = series.dropna()
    if len(clean_series) < 4:
        return (0,0.0)

    Q1 = clean_series.quantile(0.25)
    Q3 = clean_series.quantile(0.75)
    IQR = Q3-Q1
    if IQR == 0:
        return (0,0.0)

    lower = Q1-1.5*IQR
    upper = Q3+1.5*IQR
    outliers = (clean_series < lower) | (clean_series > upper)

    outlier_count = int(outliers.sum())
    outlier_percent = round((outlier_count/len(clean_series))*100,2)
    return (outlier_count,outlier_percent)


def get_top_correlations(df: pd.DataFrame, threshold: float = 0.5, top_n:int = 10) -> pd.DataFrame:
    """Find the most strongly correlated pairs of numeric columns above a given
  threshold."""
    
    result_cols = ["Feature 1", "Feature 2", "Correlation", "Absolute Correlation"]
    if df is None or df.empty:
        return pd.DataFrame(columns=result_cols)

    df_num = df.select_dtypes(include="number")
    cols = df_num.columns
    
    if len(df_num.columns) < 2:
        return pd.DataFrame(columns=result_cols)

    records = []
    corr_matrix = df_num.corr()
    for i in range(len(cols)):
        for j in range(i+1,len(cols)):
            col1,col2 = cols[i],cols[j]
            val = corr_matrix.iloc[i,j]

            if pd.notna(val) and abs(val) >= threshold:
                records.append({
                    "Feature 1": col1,
                    "Feature 2":col2,
                    "Correlation": round(float(val),3),
                    "Absolute Correlation": round(abs(float(val)),3)
                })


    if not records:
        return pd.DataFrame(columns=result_cols)
    result_df = pd.DataFrame(records)
    return (
        result_df.sort_values(by="Absolute Correlation", ascending=False).head(top_n).reset_index(drop=True)
    )


def format_context_for_llm(df: pd.DataFrame, max_sample_rows: int  = 5) -> str:
    """Generate a compact, token-efficient schema and data preview for LLM prompts.
     """
     
    if df is None or df.empty:
        return "No dataset loaded"
    rows,cols = df.shape

    lines = [
        "### Dataset Overview",
        f"-Total Rows: {rows}",
        f"-Total Columns: {cols}",
        "",
        "### Columns and Schema:",
    ]

    for col in df.columns:
        series = df[col]
        dtype = str(series.dtype)
        non_null = int(series.notna().sum())
        unique = int(series.nunique(dropna=True))

        lines.append(f"- '{col}' ({dtype}): {non_null}/{rows} non-null, {unique} unique values")

    lines.extend([
        "",
        f"### First {min(max_sample_rows, rows)} Sample Rows:",
        "```",
        df.head(max_sample_rows).to_string(index=False),
        "```",
    ])

    return "\n".join(lines)
