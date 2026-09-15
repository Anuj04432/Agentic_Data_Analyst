import streamlit as st
from utils.history import get_history,save_history

st.title("Agentic Data Analysis",text_alignment="center")

uploaded_file = st.file_uploader(label="Upload your dataset")

recent_datasets = st.selectbox(label="Recent datasets",options=["None"]+get_history())

df = None
if uploaded_file is not None or recent_datasets != "None":
    filename = uploaded_file.name if uploaded_file is not None else recent_datasets
    if uploaded_file is not None:
        save_history(uploaded_file)
        st.write(filename)

    else:
        with open(f"utils/saved_history/{recent_datasets}", "rb") as f:
            st.write("Anuj")

