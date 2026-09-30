import pandas as pd
import numpy as np

def detect_outliers_iqr(series: pd.Series, factor: float = 1.5) -> dict:

    default_dict = {
            "outlier_count": 0,
            "outlier_pct": 0.0,
            "has_outliers": False,
            "outlier_indices": [],
            "lower_bound": None,
            "upper_bound": None,
        }
    if series is None or series.empty or not pd.api.types.is_numeric_dtype(series):
        return default_dict

    cleaned_series = series.dropna()

    if len(cleaned_series) < 4:
        return default_dict

    Q1 = cleaned_series.quantile(0.25)
    Q3 = cleaned_series.quantile(0.75)
    IQR = Q3-Q1
    if IQR == 0:
        return default_dict

    lower_bound = Q1 - (factor*IQR)
    upper_bound = Q3 + (factor*IQR)

    outliers = (cleaned_series < lower_bound) | (cleaned_series > upper_bound)
    outliers_count = int(outliers.sum())
    outliers_percent = round((outliers_count/len(cleaned_series))*100,2)
    has_outliers = outliers_count > 0
    outlier_indices = cleaned_series[outliers].index.tolist()

    return {
            "outlier_count": outliers_count,
            "outlier_pct": outliers_percent,
            "has_outliers": has_outliers,
            "outlier_indices": outlier_indices,
            "lower_bound": round(float(lower_bound),4),
            "upper_bound": round(float(upper_bound),4),
        }

def detect_outliers_zscore(series: pd.Series, threshold: float = 3.0) -> dict:
    default_dict = {
        "outlier_count": 0,
        "outlier_pct": 0.0,
        "has_outliers": False,
        "outlier_indices": [],
        "threshold": float(threshold),
        "lower_bound": None,
        "upper_bound": None,
    }
    if series is None or series.empty or not pd.api.types.is_numeric_dtype(series):
        return default_dict

    cleaned_series = series.dropna()

    if len(cleaned_series) < 4:
        return default_dict

    mean = float(cleaned_series.mean())
    std = float(cleaned_series.std())

    if std == 0.0 or np.isnan(std):
        return default_dict

    lower_bound = mean - (threshold * std)
    upper_bound = mean + (threshold * std)

    outliers = (cleaned_series < lower_bound) | (cleaned_series > upper_bound)
    outliers_count = int(outliers.sum())
    outliers_percent = round((outliers_count / len(cleaned_series)) * 100, 2)
    has_outliers = outliers_count > 0
    outlier_indices = cleaned_series[outliers].index.tolist()

    return {
        "outlier_count": outliers_count,
        "outlier_pct": outliers_percent,
        "has_outliers": has_outliers,
        "outlier_indices": outlier_indices,
        "threshold": float(threshold),
        "lower_bound": round(float(lower_bound), 4),
        "upper_bound": round(float(upper_bound), 4),
    }

def get_outliers_summary(df: pd.DataFrame, method: str ="iqr") -> pd.DataFrame:
    default_cols = ["Column", "Outlier Count", "Outlier %", "Lower Bound", "Upper Bound", "Min", "Max","Has Outliers"]
    
    if df is None or df.empty:
        return pd.DataFrame(columns=default_cols)
    method = method.lower().strip()

    if method not in ["iqr","zscore"]:
        method = "iqr"

    num_cols = df.select_dtypes(include="number")
    detector = detect_outliers_iqr if method == "iqr" else detect_outliers_zscore
    outlier_df = []

    for col in num_cols:
        series = num_cols[col]
        detect_outlier = detector(series)
        outlier_df.append({
                "Column":col,
                "Outlier Count":detect_outlier["outlier_count"],
                "Outlier %": detect_outlier["outlier_pct"],
                "Lower Bound": detect_outlier["lower_bound"],
                "Upper Bound": detect_outlier["upper_bound"],
                "Min":round(float(series.min()),4) if pd.notna(series.min()) else None,
                "Max":round(float(series.max()),4) if pd.notna(series.max()) else None,
                "Has Outliers": detect_outlier["has_outliers"],
            })

    if not outlier_df:
        return pd.DataFrame(columns=default_cols)

    res_df = pd.DataFrame(outlier_df)
    return res_df.sort_values(by="Outlier Count",ascending=False).reset_index(drop=True)

