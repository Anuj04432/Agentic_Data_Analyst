import pandas as pd
import numpy as np


def get_numeric_summary(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()

    num_cols = df.select_dtypes(include="number")
    if num_cols.empty:
        return pd.DataFrame()

    result = []

    for col in num_cols:
        series = df[col].dropna()
        if series.empty:
            continue
        q25 = series.quantile(0.25)
        q75 = series.quantile(0.75)
        result.append({
            "Column":col,
            "Count":len(series),
            "Mean":series.mean(),
            "std":round(series.std(),2) if len(series)>1 else 0,
            "Variance":round(series.var(),2) if len(series)>1 else 0,
            "Min":series.min(),
            "25%(Q1)":q25,
            "50% (Median/Q2)":series.median(),
            "75%(Q3)":q75,
            "Max":series.max(),
            "IQR":q75-q25,
            "Skewness":series.skew() if len(series)>=3 else np.nan,
            "Kurtosis":series.kurt() if len(series)>=4 else np.nan
        })

    return pd.DataFrame(result)

        
def get_categorical_summary(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()

    cat_cols = df.select_dtypes(include=["object","category","string"])
    if cat_cols.empty:
        return pd.DataFrame()

    result = []
    for col in cat_cols:
        series = df[col].dropna()
        if series.empty:
            continue

        total_rows = len(df)
        missing = int(df[col].isna().sum())
        missing_percent = round((missing/total_rows)*100,2) if total_rows>0 else 0.0
        unique_values = series.nunique()
        if not series.empty:
            value_counts = series.value_counts()
            top_values = str(value_counts.index[0])
            top_values_frequency = int(value_counts.iloc[0])
            frequency_percent = round((top_values_frequency/len(series))*100,2)
        else:
            top_values = "N/A"
            top_values_frequency = 0
            frequency_percent = 0.0

        result.append({
            "Column":col,
            "Count":len(series),
            "Unique":unique_values,
            "Top value":top_values,
            "Top Frequency": top_values_frequency,
            "Top Frequency %":frequency_percent,
            "Missing" : missing,
            "Missing %": missing_percent
        })

    return pd.DataFrame(result)

def get_distribution_stats(series:pd.Series) -> dict:
    if series is None or series.empty or not pd.api.types.is_numeric_dtype(series):
        return {
            "skewness":np.nan,
            "kurtosis":np.nan,
            "skew_interpretation":"Non-numeric or empty",
            "kurt_interpretation":"Non-numeric or empty"
        }

    clean = series.dropna()
    if len(clean)<3:
        return {
            "skewness": np.nan,
            "kurtosis": np.nan,
            "skew_interpretation": "Insufficient data",
            "kurt_interpretation": "Insufficient data",
        }
    
    skew_val = float(clean.skew())
    kurt_val = float(clean.kurt()) if len(clean)>=4 else np.nan

    if abs(skew_val) < 0.5:
        skew_interp = "Fairly Symmetrical"
    elif abs(skew_val) < 1.0:
        if skew_val > 0:
            skew_interp = "Moderately Skewed (Right)"
        else:
            skew_interp = "Moderately Skewed (Left)"
    else:
        if skew_val > 0:
            skew_interp = "Highly Skewed (Right)"
        else:
            skew_interp = "Highly Skewed (Left)"

    if pd.isna(kurt_val):
        kurt_interp = "N/A"
    elif abs(kurt_val) < 0.5:
        kurt_interp = "Mesokurtic (Normal-like tails)"
    elif kurt_val >= 0.5:
        kurt_interp = "Leptokurtic (Heavy tails, prone to outliers)"
    else:
        kurt_interp = "Platykurtic (Light tails, few outliers)"

    return {
        "skewness": round(skew_val, 2),
        "kurtosis": round(kurt_val, 2) if pd.notna(kurt_val) else np.nan,
        "skew_interpretation": skew_interp,
        "kurt_interpretation": kurt_interp,
    }

    

