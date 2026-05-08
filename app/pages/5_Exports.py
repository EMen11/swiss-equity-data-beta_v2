import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from utils.load_data import load_financials, load_ratios, load_quality, load_companies, load_dictionary, load_sources
from utils.export_helpers import read_excel_bytes, dataframe_to_csv_bytes

st.set_page_config(page_title="Exports — Swiss Equity Data", layout="wide")

st.title("Exports")
st.markdown(
    "Download the full beta dataset in Excel or as individual CSV files. "
    "CSV files are the public beta data layer. Excel is the packaged user export."
)

st.markdown("### Excel Export (All Sheets)")
st.markdown(
    """
The Excel file contains the following sheets:

| Sheet | Description |
|-------|-------------|
| Financials | Normalized annual financial data |
| Ratios | Calculated financial ratios and margins |
| Data Quality | Per-field quality flags with severity |
| Company Master | Company metadata and coverage summary |
| Data Dictionary | Field definitions and formulas |
| Sources | Source manifest per company and year |
| Methodology | Notes on normalization and data collection |
"""
)

excel_bytes = read_excel_bytes()
if excel_bytes:
    st.download_button(
        label="Download swiss_equity_data_public_beta.xlsx",
        data=excel_bytes,
        file_name="swiss_equity_data_public_beta.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
else:
    st.warning("Excel export file not found. Please ensure `exports/swiss_equity_data_public_beta.xlsx` exists in the repository.")

st.divider()

st.markdown("### Individual CSV Downloads")
st.caption("These CSV files are the source data layer powering this Streamlit app.")

csv_exports = [
    ("financials.csv", load_financials, "Annual normalized financial data"),
    ("ratios.csv", load_ratios, "Calculated ratios and margins"),
    ("data_quality_report.csv", load_quality, "Per-field quality flags"),
    ("company_master.csv", load_companies, "Company metadata and coverage"),
    ("data_dictionary.csv", load_dictionary, "Field definitions"),
    ("sources.csv", load_sources, "Source manifest"),
]

for filename, loader_fn, description in csv_exports:
    df = loader_fn()
    col1, col2 = st.columns([3, 1])
    col1.markdown(f"**{filename}** — {description} ({len(df)} rows)")
    if not df.empty:
        col2.download_button(
            label=f"Download {filename}",
            data=dataframe_to_csv_bytes(df),
            file_name=filename,
            mime="text/csv",
            key=f"dl_{filename}",
        )
    else:
        col2.warning("Not available")

st.divider()
st.warning(
    "**Disclaimer:** This is a public beta. For research and analysis support only. "
    "Not investment advice. Data may contain missing fields or quality flags."
)
