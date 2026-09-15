from pathlib import Path

import streamlit as st

from data.Data_ingestion import dataset_format


st.title("Data Visualization")
st.write("Upload a dataset or select a recent dataset to explore it with charts.")

history_dir = Path(__file__).resolve().parents[1] / "data" / "history"
supported_types = ["csv", "xlsx", "xls", "json", "feather"]
recent_files = sorted(
    file.name
    for file in history_dir.glob("*")
    if file.is_file() and file.suffix.lower().lstrip(".") in supported_types
)

with st.sidebar:
    file = st.file_uploader(
        "Upload your dataset", type=supported_types, key="viz_upload"
    )
    recent_dataset = st.selectbox(
        "Recent datasets", options=[None] + recent_files, key="viz_recent"
    )

if file is None and recent_dataset is None:
    st.info("Please upload a dataset or select a recent dataset to continue.")
    st.stop()

try:
    if file is not None:
        file.seek(0)
        filename = file.name
        df = dataset_format(file, filename.lower())
    else:
        filename = recent_dataset
        with (history_dir / filename).open("rb") as saved_file:
            df = dataset_format(saved_file, filename.lower())
except Exception as error:
    st.error(f"Unable to load the dataset: {error}")
    st.stop()

if df.empty:
    st.warning("This dataset is empty. Please select another dataset.")
    st.stop()

st.caption(f"Dataset: {filename} | Rows: {df.shape[0]} | Columns: {df.shape[1]}")
with st.expander("Preview dataset"):
    st.dataframe(df.head(100))

chart_type = st.selectbox(
    "Chart type", ["Line chart", "Bar chart", "Scatter chart", "Category counts"]
)

if chart_type == "Category counts":
    column = st.selectbox("Select a column", df.columns.tolist())
    counts = df[column].dropna().astype(str).value_counts().head(20)
    if counts.empty:
        st.warning("This column has no non-missing values to plot.")
        st.stop()
    st.caption("Showing the 20 most frequent values (missing values excluded).")
    st.bar_chart(counts)
else:
    numeric_columns = df.select_dtypes(include="number").columns.tolist()
    if not numeric_columns:
        st.warning("This chart needs numeric columns. Try Category counts instead.")
        st.stop()

    x_options = numeric_columns if chart_type == "Scatter chart" else df.columns.tolist()
    col1, col2 = st.columns(2)
    with col1:
        x = st.selectbox("X-axis", x_options)
    with col2:
        y = st.selectbox("Y-axis (numeric)", numeric_columns)

    chart_data = df[list(dict.fromkeys([x, y]))].dropna()
    if chart_data.empty:
        st.warning("The selected columns have no complete rows to plot.")
        st.stop()

    if chart_type == "Line chart":
        st.line_chart(chart_data, x=x, y=y)
    elif chart_type == "Bar chart":
        chart_data = chart_data.groupby(x, as_index=True)[y].mean()
        st.caption("Showing the average Y value for each X value.")
        st.bar_chart(chart_data)
    else:
        st.scatter_chart(chart_data, x=x, y=y)
