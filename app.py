import streamlit as st
import pandas as pd

from data.Data_ingestion import dataset_format
from data.data_extract import data_info
from utils.history import save_dataset, get_dataset_history, load_dataset

st.title("Agentic Data Analysis",text_alignment="center")

with st.sidebar:
    file = st.file_uploader(label="Upload your businees dataset",type=["csv","excel","sql"],max_upload_size=500,help="Upload the files that are mentioned",label_visibility="visible",)

    sidebar = st.radio(label="Select the option",options=("Data Analysis","Data Visualization"),horizontal=True)

    if file is not None:
        filename = file.name

        
        df = dataset_format(file,filename)
        columns = df.columns
        info = data_info(df,columns)
        


        st.subheader("What you want to Know about the dataset",text_alignment="center")
        st.divider()
        select = st.multiselect(label = "Select what you want",options=["rows","columns","nullvalues","sum"])


    

        col1,col2 = st.columns(2,gap="medium")
        if "rows" in select:
            with col1:
                st.metric(label="No.of rows",value=df.shape[0])
                st.metric(label="Duplicate Rows",value=info["duplicate_rows"])
                if info["numeric_columns"]:
                    st.write("Numeric columns:",info["numeric_columns"])
                if info["categorical_columns"]:
                    st.write("categorical columns:",info["categorical_columns"])
                if info["datetime_columns"]:
                    st.write("Datetime columns:",info["datetime_columns"])

        if "columns" in select:
            with col2:
                st.metric(label="No.of Columns",value=df.shape[1])


        col_select = st.selectbox(label="which column want to select",options=columns)

        if col_select in columns:
            if pd.api.types.is_numeric_dtype(df[col_select]):
                col1,col2,col3,col4,col5 = st.columns(5)
                with col1:
                    st.metric(label="Average",value=round(df[col_select].mean()))

                    
                with col2:
                    st.metric(label="Minimum_value",value=round(df[col_select].min()))
                    
                with col3:
                    st.metric(label="Medium",value=round(df[col_select].median()))
                with col4:
                    st.metric(label="Maximum",value=round(df[col_select].max()))
                with col5:
                    st.metric(label="Sum",value=round(df[col_select].sum()))

            else:
                st.write("Select the numeric columns: ",{", ".join([i for i in columns if pd.api.types.is_numeric_dtype(df[i])])})
        


    else:
        st.warning("Please upload the file first")


