import streamlit as st

st.set_page_config(page_title="Roadmap — Swiss Equity Data", layout="wide")

st.title("Roadmap")
st.markdown("Current scope of the public beta and planned features.")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Current Beta")
    st.markdown(
        """
- Streamlit public interface
- 5 selected Swiss listed companies:
  - DKSH.SW — DKSH Holding AG
  - HIAG.SW — HIAG Immobilien Holding AG
  - SCMN.SW — Swisscom AG
  - GEBN.SW — Geberit AG
  - SIKA.SW — Sika AG
- Up to 10 years of annual fundamentals per company
- Normalized financials (revenue, EBITDA, EBIT, net income, FCF, balance sheet)
- Financial ratios (ROE, margins, leverage, valuation multiples)
- Excel and CSV exports
- Data quality metadata with per-field flags and severity
- Source manifest per company and year
- Basic analytics layer (historical charts, beta universe comparison, rule-based flags)
        """
    )

with col2:
    st.markdown("### Roadmap")
    st.markdown(
        """
- More Swiss listed companies
- Broader SMI / SPI coverage
- Python API
- Exploratory MCP layer for AI-assisted workflows
- Better public source manifests with URLs
- Richer analytics (peer grouping, multi-year trend scoring)
- Additional data quality automation
        """
    )

st.divider()

st.markdown("### Python API")
st.info(
    "A Python API is planned, but the current public beta is delivered through the Streamlit interface "
    "and exportable datasets.",
    icon="🐍",
)

st.markdown("### Exploratory MCP Layer")
st.info(
    "An exploratory MCP layer is planned to allow AI assistants and agent-based workflows to query "
    "verified Swiss equity fundamentals. This is designed for analysis support, not investment recommendations.",
    icon="🤖",
)

st.divider()

st.markdown("### Beta Universe — Covered Companies")

companies = [
    {"Ticker": "DKSH.SW", "Company": "DKSH Holding AG", "Sector": "Distribution / Services"},
    {"Ticker": "HIAG.SW", "Company": "HIAG Immobilien Holding AG", "Sector": "Real Estate"},
    {"Ticker": "SCMN.SW", "Company": "Swisscom AG", "Sector": "Telecom / Infrastructure"},
    {"Ticker": "GEBN.SW", "Company": "Geberit AG", "Sector": "Industrials / Building Products"},
    {"Ticker": "SIKA.SW", "Company": "Sika AG", "Sector": "Chemicals / Construction Materials"},
]

import pandas as pd
st.dataframe(pd.DataFrame(companies), use_container_width=True, hide_index=True)

st.divider()
st.warning(
    "**Disclaimer:** This is a public beta. For research and analysis support only. "
    "Not investment advice."
)
