import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from utils.load_data import load_companies, load_financials, load_ratios, load_quality

st.set_page_config(page_title="Overview — Swiss Equity Data", layout="wide")

# ── Header ─────────────────────────────────────────────────────────────────────
st.title("Swiss Equity Data")
st.caption("Public Beta")

st.markdown(
    """
Swiss Equity Data is a public beta for structured Swiss equity fundamentals.

The goal is to transform annual report data from selected Swiss listed companies into
normalized, comparable and exportable datasets.

This beta is not a stock-picking tool. It is a data and basic analytics layer designed to help
users explore Swiss company fundamentals faster, with transparent coverage and reliability metadata.
"""
)

st.divider()

# ── Current beta scope ─────────────────────────────────────────────────────────
st.markdown("### Current Beta Scope")

scope_col1, scope_col2 = st.columns(2)

with scope_col1:
    st.markdown(
        """
- 5 selected Swiss listed companies
- Up to 10 years of annual fundamentals
- Normalized financial metrics (revenue, EBITDA, EBIT, net income, FCF, balance sheet)
- Calculated ratios (ROE, margins, leverage, valuation multiples)
        """
    )

with scope_col2:
    st.markdown(
        """
- Historical charts and basic analytics layer
- Coverage and reliability notes with per-field documentation
- Source manifest per company and year
- Excel and CSV exports
        """
    )

st.divider()

# ── KPI cards ──────────────────────────────────────────────────────────────────
companies_df = load_companies()
financials_df = load_financials()
ratios_df = load_ratios()
quality_df = load_quality()

n_companies = len(companies_df) if not companies_df.empty else 0
first_year = int(financials_df["fiscal_year"].min()) if not financials_df.empty and "fiscal_year" in financials_df.columns else "—"
last_year = int(financials_df["fiscal_year"].max()) if not financials_df.empty and "fiscal_year" in financials_df.columns else "—"
n_fin_obs = len(financials_df) if not financials_df.empty else 0
n_ratio_obs = len(ratios_df) if not ratios_df.empty else 0
n_export_formats = 2  # Excel + CSV

col1, col2, col3, col4, col5, col6 = st.columns(6)
col1.metric("Companies", n_companies)
col2.metric("First Year", first_year)
col3.metric("Last Year", last_year)
col4.metric("Financial Observations", n_fin_obs)
col5.metric("Ratio Observations", n_ratio_obs)
col6.metric("Export Formats", n_export_formats)

# ── Reliability note (below KPIs, not as a headline metric) ───────────────────
st.markdown(
    """
> Data reliability notes are available in the **Data Coverage & Reliability** page.
> These notes document missing fields, calculated values, source coverage limits and historical comparability issues.
"""
)

n_notes = len(quality_df) if not quality_df.empty else 0
with st.expander("View reliability note count"):
    st.markdown(
        f"The dataset currently includes **{n_notes} documented coverage and reliability notes** "
        "across all companies and fiscal years. These notes are methodological context items, "
        "not data errors. See the Data Coverage & Reliability page for the full breakdown."
    )

st.divider()

# ── v5.2 product direction ────────────────────────────────────────────────────
st.markdown("### v5.2 Product Direction")
st.markdown(
    """
Swiss Equity Data now follows a four-layer direction:

1. Data Layer
2. Coverage & Reliability Layer
3. Basic Analytics Layer
4. Controlled API / MCP Access

The current public beta demonstrates the first three layers and previews the future MCP/API access layer.
"""
)

st.divider()

# ── Company coverage ───────────────────────────────────────────────────────────
st.markdown("### Company Coverage")
if not companies_df.empty:
    display_cols = [c for c in ["ticker", "company_name", "sector", "industry", "exchange", "currency", "first_year", "last_year", "years_available", "validation_status"] if c in companies_df.columns]
    st.dataframe(companies_df[display_cols], use_container_width=True, hide_index=True)
else:
    st.warning("Company master data not available.")

st.divider()

# ── Why this matters ───────────────────────────────────────────────────────────
st.markdown("### Why This Matters")
st.markdown(
    """
Swiss listed company data is often available publicly, but it is fragmented across annual reports,
different reporting formats, different fiscal-year conventions and inconsistent labels. This beta
demonstrates how that data can be cleaned, normalized and made directly usable for analysis.
"""
)

st.divider()

# ── Three layers ───────────────────────────────────────────────────────────────
st.markdown("### What This Beta Delivers")

col_a, col_b, col_c = st.columns(3)

with col_a:
    st.markdown("#### Data Layer")
    st.markdown(
        """
- Normalized annual financials (revenue, EBITDA, EBIT, net income, FCF, balance sheet items)
- Ratios (ROE, margins, debt/equity, valuation multiples)
- Up to 10 years of history per company
- CSV and Excel exports
        """
    )

with col_b:
    st.markdown("#### Coverage & Reliability Layer")
    st.markdown(
        """
- Per-field completeness scores
- Documented coverage notes and review items
- Source manifest per company and year
- Methodological notes on comparability
        """
    )

with col_c:
    st.markdown("#### Basic Analytics Layer")
    st.markdown(
        """
- Historical trend charts (financials and ratios)
- Beta universe comparison across the 5 companies
- Rule-based analytical indicators (FCF, margins, leverage)
- Interactive filtering and drill-down
        """
    )

st.divider()

# ── Roadmap preview ────────────────────────────────────────────────────────────
st.markdown("### Where This Is Going")

road_col1, road_col2 = st.columns(2)

with road_col1:
    st.markdown(
        """
- Versioned Annual Data Packs
- Broader FMP-based Swiss listed company coverage
- Python API
- Traceable PDF extraction as a validation pipeline
        """
    )

with road_col2:
    st.info(
        "A controlled MCP/API access layer is being previewed for AI-assisted workflows. "
        "The current public beta remains a Streamlit app with Excel/CSV exports, reliability notes and basic analytics.",
        icon="🤖",
    )

st.divider()

# ── Disclaimer ─────────────────────────────────────────────────────────────────
st.warning(
    "**Disclaimer:** This public beta is for research and analysis support only. "
    "It does not provide investment advice, stock recommendations, price targets or buy/sell signals. "
    "Data may contain missing fields or documented coverage notes."
)
