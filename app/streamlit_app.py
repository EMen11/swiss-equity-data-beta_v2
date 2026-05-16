import streamlit as st

st.set_page_config(
    page_title="Swiss Equity Data — Public Beta",
    page_icon="🇨🇭",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("Swiss Equity Data")
st.markdown("*Traceable Swiss equity fundamentals for analysis and AI-assisted workflows.*")

st.markdown(
    """
Explore a selected public beta universe of Swiss listed companies. Swiss Equity Data is
building a structured data layer with validated annual fundamentals, ratios, quality notes,
documented limitations and Excel/CSV exports.

A broader validated data pack is available on request, with structured Excel/CSV files,
source tracking, field-level provenance, quality notes and documented limitations.

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
| AI / MCP Preview | Controlled MCP/API access direction for AI-assisted workflows |

---
"""
)

st.info(
    "**Disclaimer:** This app is for analysis support only. "
    "It does not provide investment advice, buy/sell recommendations, stock picks or price predictions. "
    "Data may contain missing fields or documented quality notes.",
    icon="ℹ️",
)
