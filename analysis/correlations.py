import pandas as pd
import numpy as np

def calculate_correlation_matrix(df: pd.DataFrame, method: str = "pearson") -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()

    method = method.lower().strip()
    if method not in ["pearson","spearman","kendall"]:
        raise ValueError(f"Unsupported method '{method}'. Choose from: 'pearson', 'spearman','kendall'.")
    try:
        num_cols = df.select_dtypes(include="number")

        if len(num_cols.columns)<2:
            return pd.DataFrame()

        df_corr = num_cols.corr(method=method)

        return df_corr.round(2)
    except Exception:
        return pd.DataFrame()

def get_top_correlations(df: pd.DataFrame, threshold: float = 0.5, top_n:int = 10, method: str = "pearson") -> pd.DataFrame:
    cols_should=["Feature 1", "Feature 2", "Correlation", "Absolute Correlation", "Direction",
          "Strength"]
    
    if df is None or df.empty:
        return pd.DataFrame(columns=cols_should)
    corr_matrix = calculate_correlation_matrix(df,method=method)
    if corr_matrix.empty:
        return pd.DataFrame(columns=cols_should)
    cols = corr_matrix.columns

    records = []

    for i in range(0, len(cols)):
        for j in range(i+1, len(cols)):
            val = corr_matrix.iloc[i, j]
            if pd.notna(val) and abs(val) >= threshold:
                abs_val = abs(float(val))
                direction = "Positive" if val > 0 else "Negative"

                if abs_val >= 0.8:
                    strength = "Very Strong"
                elif abs_val >= 0.6:
                    strength = "Strong"
                elif abs_val >= 0.4:
                    strength = "Moderate"
                else:
                    strength = "Weak"

                records.append({
                    "Feature 1": cols[i],
                    "Feature 2": cols[j],
                    "Correlation": round(float(val), 2),
                    "Absolute Correlation": round(abs_val, 2),
                    "Direction": direction,
                    "Strength": strength,
                })

    if not records:
        return pd.DataFrame(columns=cols_should)

    result_df = pd.DataFrame(records)
    return (
        result_df.sort_values(by="Absolute Correlation", ascending=False)
        .head(top_n)
        .reset_index(drop=True)
    )


def get_target_correlations(
    df: pd.DataFrame,
    target_column: str,
    method: str = "pearson",
) -> pd.DataFrame:
    """Calculate correlation of all numerical features with a designated target column."""
    result_cols = ["Feature", "Correlation", "Absolute Correlation", "Direction", "Strength"]
    if df is None or df.empty or target_column not in df.columns:
        return pd.DataFrame(columns=result_cols)

    corr_matrix = calculate_correlation_matrix(df, method=method)
    if corr_matrix.empty or target_column not in corr_matrix.columns:
        return pd.DataFrame(columns=result_cols)

    target_series = corr_matrix[target_column].drop(labels=[target_column], errors="ignore")
    records = []

    for feature, val in target_series.items():
        if pd.notna(val):
            abs_val = abs(float(val))
            direction = "Positive" if val > 0 else "Negative"
            if abs_val >= 0.8:
                strength = "Very Strong"
            elif abs_val >= 0.6:
                strength = "Strong"
            elif abs_val >= 0.4:
                strength = "Moderate"
            else:
                strength = "Weak"

            records.append({
                "Feature": feature,
                "Correlation": round(float(val), 2),
                "Absolute Correlation": round(abs_val, 2),
                "Direction": direction,
                "Strength": strength,
            })

    if not records:
        return pd.DataFrame(columns=result_cols)

    res_df = pd.DataFrame(records)
    return (
        res_df.sort_values(by="Absolute Correlation", ascending=False)
        .reset_index(drop=True)
    )


def get_correlation_overview(df: pd.DataFrame, threshold: float = 0.5) -> dict:
    """Provide a high-level summary overview of correlations in the dataset."""
    empty_summary = {
        "numeric_column_count": 0,
        "high_correlation_count": 0,
        "strongest_positive_pair": None,
        "strongest_negative_pair": None,
        "has_high_multicollinearity": False,
    }

    if df is None or df.empty:
        return empty_summary

    corr_matrix = calculate_correlation_matrix(df)
    if corr_matrix.empty:
        return empty_summary

    top_corrs = get_top_correlations(df, threshold=threshold, top_n=100)
    positives = top_corrs[top_corrs["Direction"] == "Positive"]
    negatives = top_corrs[top_corrs["Direction"] == "Negative"]

    strongest_pos = None
    if not positives.empty:
        top_pos = positives.iloc[0]
        strongest_pos = {
            "feature_1": str(top_pos["Feature 1"]),
            "feature_2": str(top_pos["Feature 2"]),
            "correlation": float(top_pos["Correlation"]),
        }

    strongest_neg = None
    if not negatives.empty:
        top_neg = negatives.iloc[0]
        strongest_neg = {
            "feature_1": str(top_neg["Feature 1"]),
            "feature_2": str(top_neg["Feature 2"]),
            "correlation": float(top_neg["Correlation"]),
        }

    severe_collinear = top_corrs[top_corrs["Absolute Correlation"] >= 0.85]

    return {
        "numeric_column_count": len(corr_matrix.columns),
        "high_correlation_count": len(top_corrs),
        "strongest_positive_pair": strongest_pos,
        "strongest_negative_pair": strongest_neg,
        "has_high_multicollinearity": not severe_collinear.empty,
    }

    
    