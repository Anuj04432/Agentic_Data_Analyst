import streamlit as st
from utils.session_state import init_session_state,set_dataset,get_dataset,has_dataset
from utils.history import get_history,save_history,get_file_path
from utils.file_handler import dataset_format
from ui.Data_Analysis import analysis_tab
from ui.Data_Visualization import visualization


st.set_page_config(page_title="Agentic Data Analyst", layout="wide")
st.title("🤖Agentic Data Analyst",text_alignment="center")

init_session_state()

with st.sidebar:
    st.header("📂Data Source")
    uploaded_file = st.file_uploader("Upload dataset", type=["csv","xlsx","xls","json","feather","sqlite","db"])
    recent_datasets = st.selectbox("Recently used datasets",options=["None"]+get_history())

if uploaded_file is not None:
    save_history(uploaded_file)
    df = dataset_format(uploaded_file,uploaded_file.name)
    set_dataset(df,uploaded_file.name)

elif recent_datasets != "None":
    file_path = get_file_path(recent_datasets)
    df = dataset_format(file_path,recent_datasets)
    set_dataset(df, recent_datasets)

df,filename = get_dataset()

if df is not None:
    st.caption(f"Active Dataset: **{filename}** | {df.shape[0]:,} rows x {df.shape[1]} columns")