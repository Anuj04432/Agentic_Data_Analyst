import streamlit as st
import pandas as pd


from data.Data_ingestion import dataset_format
from data.data_extract import data_info
from utils.history import save_history,get_history

st.title("Agentic Data Analysis",text_alignment="center")
st.divider()
df = None
with st.sidebar:
    file = st.file_uploader(label="Upload your businees dataset",type=["csv","excel","sql"],max_upload_size=500,help="Upload the files that are mentioned",label_visibility="visible",)
    recent_datasets = st.selectbox("recent_datasets",options=["None"] + get_history())
    if file is not None or recent_datasets != "None":
        filename = file.name if file is not None else recent_datasets
        if file is not None:
             df = dataset_format(file,filename)
             save_history(file)
        else:
             with open(f"data/history/{recent_datasets}", "rb") as f:
                  df = dataset_format(f,recent_datasets)
        info = data_info(df)

    else:
        st.warning("**Please upload a dataset or select a recent dataset to proceed.**")

with st.sidebar:
     radio_select = st.radio(label="Select the option",options=("Data Analysis","Data Visualization","Ask your data"),horizontal=True)
if df is not None:
    if radio_select == "Data Analysis":
        col1,col2,col3,col4 = st.columns(4)
        with col1:
            st.metric("rows",info["shape"][0])
            st.metric("Total nulls",info["total_missing"])
        with col2:
            st.metric("columns",info["shape"][1])
            st.metric("Duplicates",info["duplicate_rows"])
            st.metric("memory",info["memory_usage"])
    
        num_cols = info["numeric_columns"]
        data = data_info(num_cols)
        values = {}
        for i in num_cols:
            values["mean"] = data["mean"]
            values["null_values"] = data["total_missing"]
            values["sum"] = data["sum"]
            values["min"] = data["min"]
            values["max"] = data["max"]
            values["std"] = data["std"]
            values["variance"] = data["variance"]
        df_values = pd.DataFrame(values)
        st.table(df_values.style.format("{:.2f}"))

            
        

    if radio_select == "Data Visualization":
        st.success(f"Datavisualization on  {filename}")
         

    
