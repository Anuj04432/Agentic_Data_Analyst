import pandas as pd
import numpy as np
import io

def data_a(file):
    df = pd.read_csv(file)
    
    return {
        "shape":df.shape,
        "columns": df.columns.to_list()
    }