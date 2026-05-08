import streamlit as st

st.set_page_config(
    page_title="Swiss Equity Data — Public Beta",
    page_icon="🇨🇭",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("Swiss Equity Data")
st.markdown("### Public Beta")

st.markdown(
    """
Swiss Equity Data is a public beta showcasing normalized annual fundamentals for selected
Swiss listed companies, enriched with transparent data quality metadata, exportable datasets
and a basic analytics layer.

---

**Use the sidebar to navigate between pages:**

| Page | Content |
|------|---------|
| Overview | Project summary, KPIs, company coverage |
| Financials | Filtered financial data table |
| Analytics | Historical charts, ratios, beta universe comparison |
| Data Quality | Quality flags, sources, methodology notes |
| Exports | Download Excel and CSV datasets |
| Roadmap | Current beta scope and planned features |

---
"""
)

st.info(
    "**Disclaimer:** This is a public beta. Data may contain missing fields or quality flags. "
    "Content is provided for research and analysis support only. "
    "This is not investment advice, not stock picking, and not a buy/sell recommendation product.",
    icon="ℹ️",
)
