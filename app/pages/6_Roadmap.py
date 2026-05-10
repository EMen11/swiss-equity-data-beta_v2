import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from utils.load_data import load_companies

st.set_page_config(page_title="Roadmap — Swiss Equity Data", layout="wide")

st.title("Roadmap")
st.markdown("Current scope of the public beta and v5.2 product direction.")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Completed")
    st.markdown(
        """
- Public Streamlit beta
- 5 companies
- Annual fundamentals
- Ratios
- Reliability notes
- Excel/CSV exports
        """
    )

with col2:
    st.markdown("### Next")
    st.markdown(
        """
- Versioned Annual Data Pack
- FMP-based expansion
- PDF extractor as traceable validation pipeline
- Python API
- Controlled MCP access
        """
    )

st.divider()

st.markdown("### Access Model")
st.markdown(
    """
Annual data packs are suited for users who want versioned Excel/CSV datasets. MCP/API access is
intended for recurring workflows where users query the maintained dataset from Python or AI-assisted tools.
"""
)

st.markdown("### Python API and Controlled MCP Access")
st.info(
    "Python API and MCP access are planned as controlled access layers. The current public beta is delivered "
    "through the Streamlit interface, reliability notes and exportable datasets.",
    icon="🤖",
)

st.divider()

st.markdown("### Beta Universe — Covered Companies")

companies_df = load_companies()
if companies_df.empty:
    st.warning("Company master data not available.")
else:
    display_cols = [
        c for c in [
            "ticker",
            "company_name",
            "sector",
            "industry",
            "exchange",
            "currency",
            "first_year",
            "last_year",
            "years_available",
            "validation_status",
        ]
        if c in companies_df.columns
    ]
    st.dataframe(companies_df[display_cols], use_container_width=True, hide_index=True)

st.divider()
st.warning(
    "**Disclaimer:** This is a public beta. For research and analysis support only. "
    "Not investment advice."
)
