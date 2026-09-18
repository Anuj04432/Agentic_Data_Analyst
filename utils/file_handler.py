import pandas as pd
import sqlite3
import os
import tempfile
from pathlib import Path


def dataset_format(file,filename: str,table_name: str = None) -> pd.DataFrame:

    if hasattr(file, "seek"):
        file.seek(0)
    filename_lower  = filename.lower()

    if filename_lower.endswith(".csv"):
        return pd.read_csv(file)

    elif filename_lower.endswith(".json"):
        return pd.read_json(file)

    elif filename_lower.endswith((".xlsx", ".xls")):
        return pd.read_excel(file)
    
    elif filename_lower.endswith(".feather"):
        return pd.read_feather(file)

    elif filename_lower.endswith((".db",".sqlite",".sqlite3")):
        if isinstance(file,(str,Path)):
            conn = sqlite3.connect(file)
            return _read_sqlite(conn, table_name)

        else:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp:
                if hasattr(file, "getvalue"):
                    tmp.write(file.getvalue())
                elif hasattr(file, "read"):
                    tmp.write(file.read())
                tmp_path = tmp.name

            try:
                conn = sqlite3.connect(tmp_path)
                return _read_sqlite(conn, table_name)
            finally:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
    else:
        raise ValueError("Unsupported file format. Please provide a valid dataset")



def _read_sqlite(conn: sqlite3.Connection, tablename: str = None) -> pd.DataFrame:
    try:
        if tablename is None:
            tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table';", conn)
            table_list = tables["name"].tolist()
            if not table_list:
                raise ValueError("Database contains no tables")

            if len(table_list) == 1:
                tablename = table_list[0]
            else:
                raise ValueError(f"Please specify a table name.. Available tables are {table_list}")

        return pd.read_sql_query(f'SELECT * FROM "{tablename}"',conn)
    finally:
        conn.close()