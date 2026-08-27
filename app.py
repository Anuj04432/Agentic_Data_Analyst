import streamlit as st

from data_analysis.data import data_a

file = st.file_uploader(label="Upload your businees dataset",type=["csv","excel","sql"],max_upload_size=500,help="Upload the files that are mentioned",label_visibility="visible")
if file is not None:
    info = data_a(file)
    col1,col2 = st.columns(2)
    rows = info["shape"]
    with col1:
        st.metric(label="Rows",value=rows[0])
    with col2:
            st.metric(label="Columns",value=rows[1])
    st.write(info["columns"])

else:
    st.warning("Please upload the file first")