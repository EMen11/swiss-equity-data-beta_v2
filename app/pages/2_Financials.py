import streamlit as st
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from utils.load_data import load_financials, load_field_provenance
from utils.export_helpers import dataframe_to_csv_bytes

st.set_page_config(page_title="Financials — Swiss Equity Data", layout="wide")

st.title("Financials")
st.markdown("Normalized annual financial data for the beta universe of Swiss listed companies.")

df = load_financials()
prov_df = load_field_provenance()

if df.empty:
    st.error("Financials data could not be loaded.")
    st.stop()

# Ensure fiscal_year is numeric
if "fiscal_year" in df.columns:
    df["fiscal_year"] = pd.to_numeric(df["fiscal_year"], errors="coerce")

# ── Company label helpers ──────────────────────────────────────────────────────
def build_label_maps(source_df: pd.DataFrame) -> tuple[dict, dict]:
    """Return (ticker_to_label, label_to_ticker) mappings."""
    t2l, l2t = {}, {}
    for _, row in source_df.drop_duplicates(subset=["ticker"]).iterrows():
        ticker = row["ticker"]
        if "company_name" in source_df.columns and pd.notna(row.get("company_name")):
            label = f"{ticker} — {row['company_name']}"
        else:
            label = ticker
        t2l[ticker] = label
        l2t[label] = ticker
    return t2l, l2t

# ── Preferred default metrics ──────────────────────────────────────────────────
PREFERRED_DEFAULTS = [
    "revenue", "ebitda", "ebit", "net_income", "eps",
    "total_assets", "total_equity", "total_debt", "cash", "net_debt",
]

id_cols = [
    c for c in
    ["ticker", "company_name", "sector", "industry", "fiscal_year", "currency", "unit",
     "extraction_status", "source_file", "notes"]
    if c in df.columns
]
numeric_cols = df.select_dtypes(include="number").columns.tolist()
selectable_metrics = [c for c in numeric_cols if c not in id_cols]
default_metrics = [c for c in PREFERRED_DEFAULTS if c in selectable_metrics] or selectable_metrics[:10]

# ── Filters ────────────────────────────────────────────────────────────────────
st.markdown("### Filters")

filter_row1_col1, filter_row1_col2 = st.columns([1, 3])

# Sector selector
with filter_row1_col1:
    if "sector" in df.columns:
        sectors = sorted(df["sector"].dropna().unique().tolist())
        selected_sector = st.selectbox("Sector", ["All sectors"] + sectors)
    else:
        selected_sector = "All sectors"

# Derive visible rows after sector filter
if selected_sector != "All sectors" and "sector" in df.columns:
    sector_df = df[df["sector"] == selected_sector]
else:
    sector_df = df

ticker_to_label, label_to_ticker = build_label_maps(sector_df)
visible_labels = sorted(ticker_to_label.values())

# Reset company selection when sector changes so the list stays consistent
prev_sector = st.session_state.get("_prev_sector", selected_sector)
if prev_sector != selected_sector:
    st.session_state["company_select"] = visible_labels
st.session_state["_prev_sector"] = selected_sector

# Initialise on first load
if "company_select" not in st.session_state:
    st.session_state["company_select"] = visible_labels

# Company selector
with filter_row1_col2:
    btn_col1, btn_col2, _ = st.columns([1, 1, 6])
    if btn_col1.button("Select all visible", key="sel_all"):
        st.session_state["company_select"] = visible_labels
    if btn_col2.button("Clear", key="sel_clear"):
        st.session_state["company_select"] = []

    # Keep only labels that are still valid after a sector change
    valid_selection = [l for l in st.session_state.get("company_select", visible_labels) if l in visible_labels]

    selected_labels = st.multiselect(
        "Company / Ticker",
        options=visible_labels,
        default=valid_selection,
        key="company_select",
        help="Search by ticker (e.g. SCMN), company name (e.g. Swisscom) or suffix (e.g. .SW).",
    )

# Convert selected labels back to tickers for dataframe filtering
selected_tickers = [label_to_ticker[l] for l in selected_labels if l in label_to_ticker]

# Row 2: year mode + metric selector
filter_row2_col1, filter_row2_col2 = st.columns([2, 3])

with filter_row2_col1:
    year_mode = st.radio(
        "Year filter mode",
        options=["Continuous range", "Specific years"],
        horizontal=True,
    )

    if "fiscal_year" in df.columns:
        available_years = sorted(df["fiscal_year"].dropna().astype(int).unique().tolist())
        min_year, max_year = available_years[0], available_years[-1]

        if year_mode == "Continuous range":
            year_range = st.slider("Fiscal Year Range", min_year, max_year, (min_year, max_year))
            selected_years = None
        else:
            selected_years = st.multiselect(
                "Fiscal Years",
                options=available_years,
                default=available_years,
                help="Select one or more non-contiguous years.",
            )
            year_range = None
    else:
        year_range = None
        selected_years = None

with filter_row2_col2:
    selected_metrics = st.multiselect(
        "Metric Columns",
        options=selectable_metrics,
        default=default_metrics,
    )

# ── Apply filters ──────────────────────────────────────────────────────────────
if not selected_tickers:
    st.warning("No companies selected. Use the selector above to choose one or more companies.")
    st.stop()

filtered = df[df["ticker"].isin(selected_tickers)].copy()

if year_range and "fiscal_year" in filtered.columns:
    filtered = filtered[
        (filtered["fiscal_year"] >= year_range[0]) & (filtered["fiscal_year"] <= year_range[1])
    ]
elif selected_years and "fiscal_year" in filtered.columns:
    filtered = filtered[filtered["fiscal_year"].isin(selected_years)]

display_cols = [c for c in id_cols + selected_metrics if c in filtered.columns]

# ── Data table ─────────────────────────────────────────────────────────────────
st.divider()

if filtered.empty:
    st.info("No rows match the current filters. Adjust the sector, company or year selection.")
else:
    st.markdown(f"### Data Table — {len(filtered):,} rows")
    st.dataframe(filtered[display_cols], use_container_width=True, hide_index=True)

    completeness_cols = [c for c in ["core_completeness_score", "full_completeness_score"] if c in filtered.columns]
    if completeness_cols:
        st.divider()
        st.markdown("### Completeness Scores")
        st.markdown("Scores show the fraction of fields populated for each company-year (e.g. `4/7` = 4 of 7 core fields present).")
        comp_id = [c for c in ["ticker", "company_name", "fiscal_year"] if c in filtered.columns]
        st.dataframe(filtered[comp_id + completeness_cols], use_container_width=True, hide_index=True)

    # ── Field-level provenance ─────────────────────────────────────────────────
    _QUALITY_BADGE = {
        "Verified":           "✅ Verified",
        "Calculated":         "🔵 Calculated",
        "Usable with notes":  "⚠️ Usable with notes",
        "documented_missing": "❌ Documented missing",
    }
    _FIELD_LABEL = {
        "revenue":        "Revenue",
        "ebitda":         "EBITDA",
        "net_income":     "Net Income",
        "eps":            "EPS",
        "free_cash_flow": "Free Cash Flow",
    }

    if not prov_df.empty:
        prov_df["fiscal_year"] = pd.to_numeric(prov_df["fiscal_year"], errors="coerce")
        active_years = filtered["fiscal_year"].dropna().unique().tolist() if "fiscal_year" in filtered.columns else []
        prov_sel = prov_df[
            prov_df["ticker"].isin(selected_tickers) &
            prov_df["fiscal_year"].isin(active_years)
        ].copy()

        if not prov_sel.empty:
            st.divider()
            st.markdown("### Field-level Provenance")
            st.caption(
                "Field-level provenance is currently available for **selected beta fields only** "
                "(revenue, EBITDA, net income, EPS, free cash flow) and covers **fiscal years 2023–2024**. "
                "Coverage will be expanded in future versions. "
                "Values shown here are read-only and are not modified by this view."
            )

            prov_sel["Quality"] = prov_sel["quality_status"].map(
                lambda s: _QUALITY_BADGE.get(str(s), str(s))
            )
            prov_sel["Field"] = prov_sel["field_name"].map(
                lambda s: _FIELD_LABEL.get(str(s), str(s))
            )
            prov_sel["Value"] = prov_sel.apply(
                lambda r: "" if r["quality_status"] == "documented_missing" else (
                    str(r["value"]) if pd.notna(r["value"]) else ""
                ),
                axis=1,
            )

            prov_table = prov_sel[[
                "ticker", "fiscal_year", "Field", "Value",
                "Quality", "source_name", "source_url", "source_page",
                "source_label", "calculation_method", "notes",
            ]].rename(columns={
                "fiscal_year":        "FY",
                "source_name":        "Source",
                "source_url":         "URL",
                "source_page":        "Page",
                "source_label":       "Label",
                "calculation_method": "Method",
                "notes":              "Notes",
            }).sort_values(["ticker", "FY", "Field"])

            with st.expander("Show provenance detail", expanded=True):
                st.dataframe(
                    prov_table,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Quality": st.column_config.TextColumn(
                            "Quality",
                            help=(
                                "✅ Verified — directly confirmed from source document.\n"
                                "🔵 Calculated — derived from reported figures (e.g. OCF minus Capex).\n"
                                "⚠️ Usable with notes — value present but requires sector or methodological context.\n"
                                "❌ Documented missing — value unavailable; reason stated in Notes."
                            ),
                        ),
                        "URL": st.column_config.LinkColumn(
                            "URL",
                            help="Source document link. Click to open and verify the original figure.",
                            display_text="Open ↗",
                        ),
                        "Page": st.column_config.TextColumn(
                            "Page",
                            help="Page reference within the source document. 'not available' means the page was not recorded during extraction.",
                        ),
                        "Method": st.column_config.TextColumn(
                            "Method",
                            help="How the value was obtained: directly reported by the company, or derived from other reported figures.",
                        ),
                        "Notes": st.column_config.TextColumn(
                            "Notes",
                            help="Caveats, limitations or extraction context for this specific field.",
                            width="large",
                        ),
                    },
                )
                st.caption(f"{len(prov_table):,} provenance record(s) for the current selection.")

    st.divider()
    st.markdown("### Download Filtered Data")
    st.download_button(
        label="Download filtered financials as CSV",
        data=dataframe_to_csv_bytes(filtered[display_cols]),
        file_name="swiss_equity_financials_filtered.csv",
        mime="text/csv",
    )

st.divider()
st.info(
    "Data is sourced from public annual reports. Missing values reflect data availability, "
    "not necessarily poor reporting quality. See the Data Quality page for detailed flags.",
    icon="ℹ️",
)
st.warning(
    "**Disclaimer:** This app is for analysis support only. "
    "It does not provide investment advice, buy/sell recommendations, stock picks or price predictions."
)
