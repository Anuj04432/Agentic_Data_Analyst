from typing import Any,Dict,List
import pandas as pd
import numpy as np
from analysis.outliers import detect_outliers_iqr, get_outliers_summary
from analysis.missing_values import get_missing_summary
from analysis.duplicates import get_duplicate_summary
from analysis.correlations import get_top_correlations
from utils.helpers import format_bytes, get_column_types



def calculate_health_score(df: pd.DataFrame) -> dict:
    """Calculate composite data quality health score (0 - 100) and letter grade."""
    default_dict ={
         "health_score": 0.0,
         "grade": "N/A",
         "deductions": {
             "missing": 0.0,
             "duplicates": 0.0,
             "outliers": 0.0,
             "constant_cols": 0.0
         },
         "summary": "Dataset is empty or None."
     }

    if df is None or df.empty:
        return default_dict

    total_rows = len(df)
    total_cols = len(df.columns)
    total_cells = total_rows*total_cols

    total_missing = int(df.isna().sum().sum())
    missing_percent = (total_missing/total_cells)*100.0 if total_cells>0 else 0.0
    deduction_missing = min(30.0, round(missing_percent*1.5,1))

    total_duplicate = int(df.duplicated().sum())
    duplicate_percent = (total_duplicate/total_rows)*100
    deduction_duplicates = min(20.0,round(duplicate_percent*2.0,1))

    num_cols = df.select_dtypes(include="number")
    total_num_cols = len(num_cols.columns)
    cols_with_serve_outliers = 0

    if total_num_cols > 0:
        for col in num_cols:
            outlier_info = detect_outliers_iqr(num_cols[col])
            if outlier_info.get("outlier_pct", 0.0) > 5.0:
                cols_with_serve_outliers +=1 

        deduction_outliers = min(20.0, round((cols_with_serve_outliers/total_num_cols)*20.0,1))
    else:
        deduction_outliers = 0.0

    constant_cols_count = 0
    if total_rows > 1:
        for col in df.columns:
            if df[col].nunique(dropna=True) <= 1:
                constant_cols_count += 1
        deduction_constant_cols = min(15.0, round(constant_cols_count*5.0,1))

    total_deduction =  round(deduction_missing + deduction_duplicates + deduction_outliers + deduction_constant_cols, 1)

    score = max(0.0, min(100.0, round(100.0 - total_deduction, 1)))

    if score >= 90.0:
        grade = "A"
    elif score >= 80.0:
        grade = "B"
    elif score >= 70.0:
        grade = "C"
    elif score >= 60.0:
        grade = "D"
    else:
        grade = "F"

    issues = []
    if deduction_missing > 0:
        issues.append(f"missing_values (-{deduction_missing})")
    if deduction_duplicates > 0:
        issues.append(f"duplicated rows (-{deduction_duplicates})")
    if deduction_outliers > 0:
        issues.append(f"severe outliers (-{deduction_outliers})")
    if deduction_constant_cols > 0:
        issues.append(f"constant columns (-{deduction_constant_cols})")

    if not issues:
        summary = "Dataset is in excellent condition with no significant data hygiene issues"
    else:
        summary = f"Grade {grade} (score: {score}/100). Penalties applied for: {', '.join(issues)}"

    return {
        "health_score":float(score),
        "grade":grade,
        "deductions":{
            "missing":float(deduction_missing),
            "duplicates":float(deduction_duplicates),
            "outliers":float(deduction_outliers),
            "constant_cols": float(deduction_constant_cols)
        },
        "summary":summary
    }


def generate_dataset_audit(df: pd.DataFrame) -> dict:
    """
    Generate master diagnostic audit aggregating shape, types, missingness,
    duplicates, outliers, health score, and actionable warnings.
    """

    if df is None or df.empty:
        return {
                "shape": {"rows": 0, "columns": 0},
                "memory": {"bytes": 0, "formatted": "0 B"},
                "column_types": {"num_cols": [], "cat_cols": [], "datetime": [],
                "boolean": [], "all": []},
                "missingness": {},
                "duplicates": {},
                "outliers": {},
                "health": calculate_health_score(None),
                "warnings": ["Dataset is empty or None."],
            }

    total_row = len(df)
    total_cols = len(df.columns)
    memory_bytes = int(df.memory_usage(deep=True).sum())
    total_cells = total_row * total_cols

    col_types = get_column_types(df)
    missing_overview = get_missing_summary(df)
    duplicates_info = get_duplicate_summary(df)
    outliers_df = get_outliers_summary(df, method="iqr")
    health = calculate_health_score(df)

    warnings: List[str] = []

    for col in df.columns:
        col_missing = df[col].isna().sum()
        pct = (col_missing / total_row) * 100.0
        if pct > 30.0:
            warnings.append(f"High missing data ({pct:.1f}%) in column: '{col}'")

        if total_row > 1 and df[col].nunique(dropna=True) <= 1:
            warnings.append(f"Column '{col}' is constant/zero variance")

    dup_count = duplicates_info.get("duplicate_count", 0)
    dup_pct = duplicates_info.get("duplicate_pct", 0)
    if dup_count > 0:
        warnings.append(f"Found {dup_count} duplicate rows ({dup_pct:.1f}% of dataset)")

    if not outliers_df.empty:
        severe_cols = outliers_df[outliers_df["Outlier %"] > 5.0]
        for _, row in severe_cols.iterrows():
            warnings.append(f"Severe outliers detected in '{row['Column']}' ({row['Outlier %']:.1f}% of values)")

    top_corr = get_top_correlations(df, threshold=0.85, top_n=5)
    if not top_corr.empty:
        for _, row in top_corr.iterrows():
            warnings.append(f"High multicollinearity detected between '{row['Feature 1']}' and '{row['Feature 2']}' (r = {row['Correlation']})")

    return {
        "shape": {"rows": total_row, "columns": total_cols},
        "memory": {
            "bytes": memory_bytes,
            "formatted": format_bytes(memory_bytes)
        },
        "column_types": col_types,
        "missingness": missing_overview,
        "duplicates": {
            "duplicate_count": dup_count,
            "duplicate_pct": dup_pct,
            "has_duplicates": duplicates_info.get("has_duplicates", False)
        },
        "outliers": {
            "outliers_columns_count": int((outliers_df["Has Outliers"] == True).sum()) if not outliers_df.empty else 0,
            "summary_table": outliers_df,
        },
        "health": health,
        "warnings": warnings
    }