import pandas as pd
import numpy as np
import sqlite3

def dataset_format(file,filename,table_name = None):
    if filename.endswith(".csv"):
        df = pd.read_csv(file)
        return df

    elif filename.endswith(".xlsx") or filename.endswith(".xls"):
        df = pd.read_excel(file)
        return df
    

    elif filename.endswith(".json"):
        df = pd.read_json(file)
        return df 

    elif filename.endswith(".feather"):
        df = pd.read_feather(file)
        return df

    elif filename.endswith(".db") or filename.endswith(".sqlite3"):
        conn = sqlite3.connect(file)
        if table_name is None:
            tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table';",conn)
            raise ValueError(f"Please specify a table_name. Available tables: {tables['name'].tolist()}")
        df = pd.read_sql_query(f"SELECT * FROM {table_name}",conn)
        conn.close()
        return df

    else:
        raise ValueError("Please provide a valid dataset")