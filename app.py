import streamlit as st
import pandas as pd

from data.Data_ingestion import dataset_format
from data.data_extract import data_info
from utils.history import save_history,get_history

st.title("Agentic Data Analysis",text_alignment="center")
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
                  
        columns = df.columns
        info = data_info(df,columns)

    else:
        st.warning("**Please upload a dataset or select a recent dataset to proceed.**")

with st.sidebar:
     radio_select = st.radio(label="Select the option",options=("Data Analysis","Data Visualization","Ask your data"),horizontal=True)
if df is not None:
    if radio_select == "Data Analysis":
        st.write(df.columns)
    if radio_select == "Data Visualization":
        st.success(f"Datavisualization on  {filename}")
         

    
