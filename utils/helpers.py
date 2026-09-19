import pandas as pd


def format_bytes(size_bytes: int | float) -> str:
    if size_bytes is None or size_bytes<=0:
        return "0 B"

    for unit in ["B","KB","MB","GB","TB"]:
        if abs(size_bytes) < 1024.0:
            return f"{size_bytes:.2f} {unit}" if unit != "B" else f"{int(size_bytes)} B"
        size_bytes /= 1024.0

    return f"{size_bytes:.2f} PB"

def format_number(val: int | float | None, decimal: int = 2) -> str:
    if val is None or pd.isna(val):
        return "N/A"

    if isinstance(val, (int,)):
        return f"{val:,}"

    return f"{val:,.{decimal}f}"