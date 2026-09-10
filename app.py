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

        radio_select = st.radio(label="Select the option",options=("Data Analysis","Data Visualization","Ask your data"),horizontal=True)
        # select = st.selectbox("Select the columns",options=[None] + list(df.columns))
        # st.write(df[select].dtype)
        

    else:
        st.warning("**Please upload a dataset or select a recent dataset to proceed.**")


# -------------- Tabs -------------------

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
        
        values = {
            "mean": info["mean"],
            "null_values": num_cols.isnull().sum(),
            "sum": info["sum"],
            "min": info["min"],
            "max": info["max"],
            "median": info["median"],
            "std": info["std"],
            "dtype": num_cols.dtypes.astype(str)
        }
        
        df_values = pd.DataFrame(values)
        format_subset = [col for col in df_values.columns if col != "dtype"]
        st.table(df_values.style.format(formatter="{:.2f}", subset=format_subset),height="stretch",width="stretch",border=True)
        st.table(data=info["categorical_summary"])

        


    

if radio_select == "Data Visualization":
        st.success(f"Datavisualization on  {filename}")
        with st.sidebar:
             x = st.selectbox(label="Select the column for x-axis",options=[None]+list(df.columns))
             y = st.selectbox(label="Select the column for x-axis",options=[None]+list(df.columns),key="name")
        st.line_chart(data=df,x=x,y=y)
            



    
