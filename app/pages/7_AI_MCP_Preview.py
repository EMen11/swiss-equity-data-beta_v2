from pathlib import Path

import streamlit as st


st.set_page_config(page_title="AI / MCP Preview — Swiss Equity Data", layout="wide")

ROOT_DIR = Path(__file__).resolve().parents[2]
CLAUDE_MCP_IMAGE = ROOT_DIR / "docs" / "images" / "claude_mcp_demo.png"


st.title("AI / MCP Preview")

st.markdown(
    """
Swiss Equity Data is being extended with a controlled MCP/API access layer, designed to let
users query the structured dataset from Claude, Cursor, Kimi or other AI-assisted workflows.

The goal is not to create an autonomous financial assistant. The MCP layer exposes controlled
functions on top of structured, checked and exportable Swiss equity data.
"""
)

st.divider()

st.markdown("### Current beta vs next access layer")

current_col, next_col = st.columns(2)

with current_col:
    st.markdown("#### Current public beta")
    st.markdown(
        """
- Streamlit web interface
- 5 selected Swiss listed companies
- Normalized annual fundamentals
- Ratios and basic analytics
- Data Coverage & Reliability notes
- Excel / CSV exports
        """
    )

with next_col:
    st.markdown("#### Next access layer")
    st.markdown(
        """
- Python API
- MCP server
- Controlled AI-assisted querying
- Comparables generation
- Quality report queries
- Export generation from structured data
        """
    )

st.divider()

st.markdown("### Example MCP workflow")

if CLAUDE_MCP_IMAGE.exists():
    st.image(
        str(CLAUDE_MCP_IMAGE),
        caption="Example MCP workflow in Claude Desktop using swiss-equity-data.",
        use_container_width=True,
    )
else:
    st.info("Claude Desktop MCP workflow screenshot will be added here.")

st.divider()

st.markdown("### Example questions")
st.markdown(
    """
- Compare DKSH.SW, GEBN.SW and SIKA.SW for 2025.
- Show the quality report for HIAG.SW.
- Generate a comparables table for selected Swiss listed companies.
- Which companies have missing EBITDA values?
- Export EV/EBITDA by year for selected tickers.
"""
)

st.divider()

st.markdown("### Controlled functions")
st.code(
    """
get_companies()
get_company_profile(ticker)
get_fundamentals(ticker, years=10)
get_ratios(ticker, years=10)
get_quality_report(ticker)
compare_companies(tickers, metrics, years=10)
get_sector_comparables(ticker)
screen_companies(filters)
export_company_data(ticker)
export_comparables(tickers)
""".strip(),
    language="python",
)

st.divider()

st.markdown("### Guardrails")
st.markdown(
    """
The MCP layer is designed for analysis support only. It does not provide buy/sell
recommendations, personalized investment advice, stock picks or price predictions.
Financial calculations remain deterministic and should be backed by structured data,
sources and reliability notes.
"""
)

st.markdown("Examples of requests to refuse or reframe:")
st.markdown(
    """
- Should I buy DKSH?
- Which stock will outperform?
- Give me the best Swiss small caps to buy.
- Predict Sika's share price.
"""
)
