import streamlit as st
import pandas as pd
import requests
from datetime import datetime

st.set_page_config(page_title="CA Advisory AI", page_icon="📊", layout="wide")

# TODO: Replace this with your Google Sheet ID
SHEET_ID = "1NZqi-IwYRpWc9VAFevx5yY-53c1NEQFm2aEfHd3czGA"

def get_sheet_tab_data(tab_name):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={tab_name}"
    resp = requests.get(url)
    resp.raise_for_status()
    from io import StringIO
    return pd.read_csv(StringIO(resp.text))

st.title("📊 CA Advisory AI")
st.caption("ICAI AI Hackathon Season 6 – Prototype")

st.markdown("### 1. Load sample data from Google Sheet")

try:
    clients_df = get_sheet_tab_data("Clients")
    workspaces_df = get_sheet_tab_data("Workspaces")
    uploads_df = get_sheet_tab_data("Uploads")

    st.success("Google Sheet connected successfully.")
    st.write("**Clients:**")
    st.dataframe(clients_df.head())
    st.write("**Workspaces:**")
    st.dataframe(workspaces_df.head())
    st.write("**Uploads:**")
    st.dataframe(uploads_df.head())
except Exception as e:
    st.error(f"Error loading data from Google Sheet: {e}")
    st.info("Check that:")
    st.markdown("- The Sheet ID is correct in `app.py`.")
    st.markdown("- The sheet is shared as **Anyone with the link can view**.")
    st.markdown("- Tab names are exactly: `Clients`, `Workspaces`, `Uploads`.")

st.markdown("---")
st.markdown("### 2. Upload Trial Balance (demo only – not yet processed)")

uploaded_file = st.file_uploader("Choose an Excel file", type=["xlsx"])

if uploaded_file is not None:
    st.info("File uploaded. Processing will be added in the next session.")
    st.write("File name:", uploaded_file.name)
    st.write("Size (bytes):", uploaded_file.size)
