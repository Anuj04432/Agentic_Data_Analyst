from data.open_dataset import dataset_format
import pandas as pd

def data_info(df):
    data_shape = df.shape


    info = {
        "describe":df.describe(),
        "columns":df.columns,
        "no_rows":data_shape[0],
        "no_colums":data_shape[1],
        "nullvalues":df.isnull().sum(),
        "dtypes": df.dtypes,
        # "sum":{i: round(df[i].sum().item(),2)
        #        for i in df.columns
        #        if pd.api.types.is_numeric_dtype(df[i])},
        "sum1": df.select_dtypes(include="number").sum()
    }
    return info