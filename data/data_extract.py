from data.Data_ingestion import dataset_format
import pandas as pd

def data_info(df):
    
    info = {
        # Dataset
        "shape": df.shape,
        "memory_usage": df.memory_usage(deep=True).sum(),
        
        # Missing data
        "total_missing": df.isnull().sum().sum(),
        "missing_percentage": (
            df.isnull().sum() / len(df) * 100
        ).round(2),

        # Duplicates
        "duplicate_rows": df.duplicated().sum(),

        # Columns
        "numeric_columns": df.select_dtypes(include="number"),
        "categorical_columns": df.select_dtypes(include="object").columns,
        "datetime_columns": df.select_dtypes(include="datetime").columns,

        # Cardinality
        "unique_values": df.nunique(),
        
        # Numeric
        "sum": df.select_dtypes(include="number").sum(),
        "mean": df.select_dtypes(include="number").mean(),
        "median": df.select_dtypes(include="number").median(),
        "min": df.select_dtypes(include="number").min(),
        "max": df.select_dtypes(include="number").max(),
        "std": df.select_dtypes(include="number").std(),
        "variance": df.select_dtypes(include="number").var(),

        # Relationships
        "correlation": df.select_dtypes(include="number").corr(),

        # Statistical distribution
        "skewness": df.select_dtypes(include="number").skew(),
        "kurtosis": df.select_dtypes(include="number").kurt(),

        # Categorical
        "categorical_summary": {
            col: df[col].value_counts().head(10)
            for col in df.select_dtypes(include="object").columns
        }
    }
    return info