import streamlit as st

from data.open_dataset import dataset_format
from data.data_extract import data_info

file = st.file_uploader(label="Upload your businees dataset",type=["csv","excel","sql"],max_upload_size=500,help="Upload the files that are mentioned",label_visibility="visible")
if file is not None:
    filename = file.name
    df = dataset_format(file,filename)
    df = data_info(df)

    st.write(df["columns"])
    st.write(df["dtypes"])
    st.write(df["sum1"])
    st.write(df["sum"])
    st.write("Null values are in the dataset",df["nullvalues"])
    st.metric(label="rows",value=df["no_rows"])
    
   


else:
    st.warning("Please upload the file first")