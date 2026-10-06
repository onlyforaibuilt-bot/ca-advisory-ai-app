import streamlit as st
import pandas as pd
import requests
from io import BytesIO, StringIO
from datetime import datetime

st.set_page_config(page_title="CA Advisory AI", page_icon="📊", layout="wide")

# TODO: Replace this with your Google Sheet ID
SHEET_ID = "1NZqi-IwYRpWc9VAFevx5yY-53c1NEQFm2aEfHd3czGA"

def get_sheet_tab_data(tab_name):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={tab_name}"
    resp = requests.get(url)
    resp.raise_for_status()
    return pd.read_csv(StringIO(resp.text))

def calculate_basic_metrics(tb_df: pd.DataFrame):
    """
    tb_df must have columns: Year, AccountName, Group, DebitCredit, Amount
    Returns a DataFrame with basic metrics per year.
    """
    # Ensure Amount is numeric
    tb_df["Amount"] = pd.to_numeric(tb_df["Amount"], errors="coerce").fillna(0)

    # Separate DR and CR
    dr = tb_df[tb_df["DebitCredit"] == "DR"].copy()
    cr = tb_df[tb_df["DebitCredit"] == "CR"].copy()

    # Revenue = sum of CR where Group == "Revenue"
    revenue = (
        cr[cr["Group"] == "Revenue"]
        .groupby("Year")["Amount"]
        .sum()
        .reset_index()
        .rename(columns={"Amount": "Revenue"})
    )

    # Direct expenses = sum of DR where Group == "DirectExpenses"
    direct_exp = (
        dr[dr["Group"] == "DirectExpenses"]
        .groupby("Year")["Amount"]
        .sum()
        .reset_index()
        .rename(columns={"Amount": "DirectExpenses"})
    )

    # Indirect expenses = sum of DR where Group == "IndirectExpenses"
    indirect_exp = (
        dr[dr["Group"] == "IndirectExpenses"]
        .groupby("Year")["Amount"]
        .sum()
        .reset_index()
        .rename(columns={"Amount": "IndirectExpenses"})
    )

    # Merge
    metrics = revenue.merge(direct_exp, on="Year", how="outer").merge(
        indirect_exp, on="Year", how="outer"
    )
    metrics = metrics.fillna(0)

    # Gross Profit = Revenue - DirectExpenses
    metrics["GrossProfit"] = metrics["Revenue"] - metrics["DirectExpenses"]
    # Net Profit (simplified) = Revenue - DirectExpenses - IndirectExpenses
    metrics["NetProfit"] = metrics["Revenue"] - metrics["DirectExpenses"] - metrics["IndirectExpenses"]

    # Margins
    metrics["GrossMarginPct"] = (
        (metrics["GrossProfit"] / metrics["Revenue"]).replace([float("inf"), -float("inf")], 0) * 100
    )
    metrics["NetMarginPct"] = (
        (metrics["NetProfit"] / metrics["Revenue"]).replace([float("inf"), -float("inf")], 0) * 100
    )

    return metrics

st.title("📊 CA Advisory AI")
st.caption("ICAI AI Hackathon Season 6 – Prototype")

st.markdown("### 1. Load sample data from Google Sheet")

try:
    clients_df = get_sheet_tab_data("Clients")
    workspaces_df = get_sheet_tab_data("Workspaces")
    uploads_df = get_sheet_tab_data("Uploads")

    st.success("Google Sheet connected successfully.")
    with st.expander("View Clients"):
        st.dataframe(clients_df.head())
    with st.expander("View Workspaces"):
        st.dataframe(workspaces_df.head())
    with st.expander("View Uploads"):
        st.dataframe(uploads_df.head())
except Exception as e:
    st.error(f"Error loading data from Google Sheet: {e}")
    st.info("Check that:")
    st.markdown("- The Sheet ID is correct in `app.py`.")
    st.markdown("- The sheet is shared as **Anyone with the link can view**.")
    st.markdown("- Tab names are exactly: `Clients`, `Workspaces`, `Uploads`.")

st.markdown("---")
st.markdown("### 2. Upload Trial Balance (Excel)")

uploaded_file = st.file_uploader("Choose an Excel file", type=["xlsx"])

if uploaded_file is not None:
    st.info("File uploaded. Reading and calculating basic metrics...")

    try:
        # Read Excel
        tb_df = pd.read_excel(uploaded_file, sheet_name="TrialBalance")
        st.success("Trial Balance read successfully.")

        # Show raw data in an expander
        with st.expander("View uploaded Trial Balance"):
            st.dataframe(tb_df.head(10))

        # Calculate metrics
        metrics_df = calculate_basic_metrics(tb_df)

        st.markdown("### 3. Basic Financial Metrics (from uploaded TB)")
        st.dataframe(metrics_df)

        st.markdown("#### Simple interpretation")
        if not metrics_df.empty:
            latest = metrics_df.iloc[-1]
            st.write(
                f"Latest year ({int(latest['Year'])}): "
                f"Revenue = {latest['Revenue']:,.0f}, "
                f"Gross Profit = {latest['GrossProfit']:,.0f}, "
                f"Net Profit = {latest['NetProfit']:,.0f}. "
                f"Gross Margin = {latest['GrossMarginPct']:.1f}%, "
                f"Net Margin = {latest['NetMarginPct']:.1f}%."
            )
        else:
            st.warning("No metrics calculated. Check your Trial Balance structure.")

    except Exception as e:
        st.error(f"Error processing the uploaded file: {e}")
        st.info("Make sure the Excel file has a sheet named 'TrialBalance' with columns: Year, AccountName, Group, DebitCredit, Amount.")
