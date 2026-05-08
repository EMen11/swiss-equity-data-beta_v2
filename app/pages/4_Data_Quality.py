import streamlit as st
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from utils.load_data import load_quality, load_sources, load_companies

st.set_page_config(page_title="Data Coverage & Reliability — Swiss Equity Data", layout="wide")

st.title("Data Coverage & Reliability")

# ── Introduction ───────────────────────────────────────────────────────────────
st.markdown(
    """
This page documents the coverage, review notes and known limitations of the public beta dataset.
Notes are used to separate methodological context from items that may require review.

Most notes are not data errors. They indicate missing optional fields, calculated values,
source coverage limits or historical comparability issues.
"""
)

# ── How to interpret these notes ──────────────────────────────────────────────
st.markdown("#### How to interpret these notes")
st.markdown(
    """
- **Missing field** — a value is not available in the public beta dataset.
- **Calculated value** — the value is derived from available components.
- **Comparability note** — historical comparison may be affected by splits, scope changes or reporting changes.
- **Review item** — the value or context should be checked before detailed analysis.
- **Methodology note** — informational context, not an error.
"""
)

# ── Glossary expander ──────────────────────────────────────────────────────────
with st.expander("Note type reference"):
    st.markdown(
        """
| Note type | Meaning |
|-----------|---------|
| `missing_public_field` | A field is not available in the public beta dataset |
| `missing_free_cash_flow_final` | Final FCF figure is absent — operating cash flow and capex were unavailable |
| `free_cash_flow_calculated` | FCF is derived from operating cash flow and capex, not reported directly |
| `negative_cash` | Reported or extracted cash value is negative and requires context |
| `missing_dividend_yield` | Dividend yield could not be calculated (price or dividend data missing) |
| `missing_capex` | Capital expenditure data is not available for this company-year |
| `per_share_not_comparable_pre_split` | Per-share figures are not comparable across the full history due to share splits |

**Note categories:**

- **Review item** — the value or context warrants review before use *(raw value: `warning`)*
- **Methodology note** — informational context; the data may still be valid but has a known limitation *(raw value: `info`)*
        """
    )

st.divider()

quality_df = load_quality()
sources_df = load_sources()
companies_df = load_companies()

# ── Label helpers ──────────────────────────────────────────────────────────────
def build_label_maps(*candidate_dfs: pd.DataFrame) -> tuple[dict, dict]:
    t2l, l2t = {}, {}
    for df in candidate_dfs:
        if df.empty or "ticker" not in df.columns:
            continue
        has_name = "company_name" in df.columns
        for ticker, grp in df.groupby("ticker"):
            if str(ticker) in t2l:
                continue
            name = None
            if has_name:
                non_null = grp["company_name"].dropna()
                name = non_null.iloc[0] if not non_null.empty else None
            label = f"{ticker} — {name}" if name else str(ticker)
            t2l[str(ticker)] = label
            l2t[label] = str(ticker)
    return t2l, l2t

ticker_to_label, label_to_ticker = build_label_maps(quality_df, companies_df, sources_df)

def ticker_label(ticker: str) -> str:
    return ticker_to_label.get(str(ticker), str(ticker))


# ── Readable note type mapping ─────────────────────────────────────────────────
NOTE_LABELS: dict[str, str] = {
    "missing_public_field": "Missing public field",
    "missing_free_cash_flow_final": "Missing final FCF",
    "free_cash_flow_calculated": "Free cash flow calculated",
    "negative_cash": "Negative cash value",
    "missing_dividend_per_share": "Missing dividend per share",
    "missing_dividend_yield": "Missing dividend yield",
    "missing_capex": "Missing capex",
    "per_share_not_comparable_pre_split": "Per-share data not comparable",
}

SEVERITY_DISPLAY: dict[str, str] = {
    "warning": "Review item",
    "info": "Methodology note",
}

def readable_note_type(raw: str) -> str:
    if pd.isna(raw):
        return ""
    return NOTE_LABELS.get(str(raw), str(raw).replace("_", " ").title())

def display_severity(raw: str) -> str:
    if pd.isna(raw):
        return ""
    return SEVERITY_DISPLAY.get(str(raw), str(raw).replace("_", " ").title())


# ── Documented Notes & Review Items section ────────────────────────────────────
st.markdown("### Documented Notes & Review Items")

if quality_df.empty:
    st.warning("Coverage and reliability data not available.")
else:
    sev_col = "quality_level" if "quality_level" in quality_df.columns else None

    # ── KPI cards ──────────────────────────────────────────────────────────────
    total_notes = len(quality_df)
    review_items   = int((quality_df[sev_col] == "warning").sum()) if sev_col else "—"
    method_notes   = int((quality_df[sev_col] == "info").sum())    if sev_col else "—"
    companies_covered = quality_df["ticker"].nunique() if "ticker" in quality_df.columns else "—"
    years_covered     = quality_df["fiscal_year"].nunique() if "fiscal_year" in quality_df.columns else "—"

    kc1, kc2, kc3, kc4, kc5 = st.columns(5)
    kc1.metric("Documented notes", total_notes)
    kc2.metric("Review items", review_items)
    kc3.metric("Methodology notes", method_notes)
    kc4.metric("Companies covered", companies_covered)
    kc5.metric("Fiscal years covered", years_covered)

    st.divider()

    # ── Filters ────────────────────────────────────────────────────────────────
    fc1, fc2, fc3, fc4 = st.columns(4)

    with fc1:
        if "ticker" in quality_df.columns:
            all_tickers = sorted(quality_df["ticker"].dropna().unique().tolist())
            all_company_labels = sorted(ticker_label(t) for t in all_tickers)
            company_label_to_ticker = {ticker_label(t): t for t in all_tickers}

            sel_company_labels = st.multiselect(
                "Company",
                options=all_company_labels,
                default=all_company_labels,
                key="q_ticker",
                help="Search by ticker or company name.",
            )
            sel_tickers = [company_label_to_ticker[l] for l in sel_company_labels if l in company_label_to_ticker]
        else:
            sel_tickers = []

    with fc2:
        if "fiscal_year" in quality_df.columns:
            years = sorted(quality_df["fiscal_year"].dropna().unique().tolist())
            sel_years = st.multiselect("Fiscal Year", years, default=years, key="q_year")
        else:
            sel_years = None

    issue_col = next((c for c in ["issue_type", "flag", "category"] if c in quality_df.columns), None)

    with fc3:
        if issue_col:
            issues = sorted(quality_df[issue_col].dropna().unique().tolist())
            note_label_map = {readable_note_type(i): i for i in issues}
            sel_note_labels = st.multiselect(
                "Note type",
                options=sorted(note_label_map.keys()),
                default=sorted(note_label_map.keys()),
                key="q_issue",
            )
            sel_issues = [note_label_map[l] for l in sel_note_labels if l in note_label_map]
        else:
            sel_issues = None

    with fc4:
        if sev_col:
            # Show display labels, map back to raw values for filtering
            raw_severities = sorted(quality_df[sev_col].dropna().unique().tolist())
            sev_display_map = {display_severity(s): s for s in raw_severities}
            sel_sev_labels = st.multiselect(
                "Note category",
                options=sorted(sev_display_map.keys()),
                default=sorted(sev_display_map.keys()),
                key="q_sev",
            )
            sel_severities = [sev_display_map[l] for l in sel_sev_labels if l in sev_display_map]
        else:
            sel_severities = None

    # ── Apply filters ──────────────────────────────────────────────────────────
    if not sel_tickers and "ticker" in quality_df.columns:
        st.info("No companies selected. Select at least one company to display notes.")
        st.stop()

    filtered_q = quality_df.copy()
    if sel_tickers and "ticker" in filtered_q.columns:
        filtered_q = filtered_q[filtered_q["ticker"].isin(sel_tickers)]
    if sel_years and "fiscal_year" in filtered_q.columns:
        filtered_q = filtered_q[filtered_q["fiscal_year"].isin(sel_years)]
    if sel_issues and issue_col:
        filtered_q = filtered_q[filtered_q[issue_col].isin(sel_issues)]
    if sel_severities and sev_col:
        filtered_q = filtered_q[filtered_q[sev_col].isin(sel_severities)]

    # Build display frame — readable columns first, raw technical columns retained
    display_q = filtered_q.copy()
    if issue_col and issue_col in display_q.columns:
        insert_pos = display_q.columns.tolist().index(issue_col) + 1
        display_q.insert(insert_pos, "note_type", display_q[issue_col].map(readable_note_type))
    if sev_col and sev_col in display_q.columns:
        insert_pos = display_q.columns.tolist().index(sev_col) + 1
        display_q.insert(insert_pos, "display_severity", display_q[sev_col].map(display_severity))

    if display_q.empty:
        st.info("No notes match the current filters.")
    else:
        st.dataframe(display_q, use_container_width=True, hide_index=True)
        st.caption(f"{len(display_q):,} documented notes shown.")

    # ── Summary breakdown ──────────────────────────────────────────────────────
    st.divider()
    st.markdown("### Summary")

    sum_col1, sum_col2 = st.columns(2)

    with sum_col1:
        if "ticker" in quality_df.columns:
            st.markdown("**Notes by company**")
            by_ticker = (
                quality_df.groupby("ticker").size()
                .reset_index(name="notes")
                .sort_values("notes", ascending=False)
            )
            by_ticker.insert(0, "company", by_ticker["ticker"].map(ticker_label))
            st.dataframe(by_ticker, use_container_width=True, hide_index=True)

    with sum_col2:
        if issue_col:
            st.markdown("**Notes by type**")
            by_type = (
                quality_df.groupby(issue_col).size()
                .reset_index(name="notes")
                .sort_values("notes", ascending=False)
            )
            by_type["note_type"] = by_type[issue_col].map(readable_note_type)
            by_type = by_type[["note_type", issue_col, "notes"]]
            st.dataframe(by_type, use_container_width=True, hide_index=True)

st.divider()

# ── Source coverage ────────────────────────────────────────────────────────────
st.markdown("### Source Coverage")
st.info(
    "Source manifests are being expanded as the public beta evolves. "
    "The dataset currently tracks source files and extraction metadata, "
    "while public source URLs may be incomplete for some companies.",
    icon="ℹ️",
)

if sources_df.empty:
    st.warning("Sources data not available.")
else:
    source_display = (
        sources_df[sources_df["ticker"].notna()].copy()
        if "ticker" in sources_df.columns
        else sources_df.copy()
    )

    if "ticker" in source_display.columns:
        source_display.insert(1, "company", source_display["ticker"].map(ticker_label))

    src_rows = len(source_display)
    src_companies = source_display["ticker"].nunique() if "ticker" in source_display.columns else "—"

    if "source_url" in source_display.columns:
        src_urls_available = int(source_display["source_url"].notna().sum())
        src_urls_missing   = int(source_display["source_url"].isna().sum())
    else:
        src_urls_available = "—"
        src_urls_missing   = "—"

    sc1, sc2, sc3, sc4 = st.columns(4)
    sc1.metric("Source records", src_rows)
    sc2.metric("Companies covered", src_companies)
    sc3.metric("Source URLs available", src_urls_available)
    sc4.metric("Source URLs pending", src_urls_missing)

    st.dataframe(source_display, use_container_width=True, hide_index=True)

st.divider()
st.warning(
    "**Disclaimer:** This is a public beta. For research and analysis support only. "
    "Not investment advice."
)
