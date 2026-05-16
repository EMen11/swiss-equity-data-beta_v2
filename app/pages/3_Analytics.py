import streamlit as st
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from utils.load_data import load_financials, load_ratios
from utils.charts import line_chart, beta_universe_bar

st.set_page_config(page_title="Analytics — Swiss Equity Data", layout="wide")

st.title("Analytics")
st.markdown("Interactive charts and beta universe comparison for Swiss listed companies.")

fin_df = load_financials()
rat_df = load_ratios()

if fin_df.empty and rat_df.empty:
    st.error("Could not load data for analytics.")
    st.stop()

# ── Label helpers ──────────────────────────────────────────────────────────────
def build_label_maps(source_df: pd.DataFrame) -> tuple[dict, dict]:
    """Return (ticker_to_label, label_to_ticker) from the first non-null company_name per ticker."""
    t2l, l2t = {}, {}
    has_name = "company_name" in source_df.columns
    for ticker, grp in source_df.groupby("ticker"):
        if has_name:
            name_series = grp["company_name"].dropna()
            name = name_series.iloc[0] if not name_series.empty else None
        else:
            name = None
        label = f"{ticker} — {name}" if name else str(ticker)
        t2l[str(ticker)] = label
        l2t[label] = str(ticker)
    return t2l, l2t

source_for_labels = fin_df if not fin_df.empty else rat_df
ticker_to_label, label_to_ticker = build_label_maps(source_for_labels)
all_labels = sorted(ticker_to_label.values())

# ── Main company selector ──────────────────────────────────────────────────────
sel_col, cap_col = st.columns([2, 5])
with sel_col:
    selected_label = st.selectbox(
        "Select Company",
        options=all_labels,
        help="Search by ticker (e.g. SCMN), company name (e.g. Swisscom) or suffix (e.g. .SW).",
    )
    st.caption("Search by ticker or company name.")

selected_ticker = label_to_ticker.get(selected_label, selected_label)

st.divider()

tab1, tab2, tab3, tab4 = st.tabs(["Historical Trends", "Ratios", "Beta Universe Comparison", "Analytical Flags"])

# ── Tab 1: Historical Trends ──────────────────────────────────────────────────
with tab1:
    st.markdown(f"### Historical Financials — {selected_label}")
    if fin_df.empty:
        st.warning("Financials not available.")
    else:
        ticker_fin = fin_df[fin_df["ticker"] == selected_ticker].sort_values("fiscal_year")

        fin_metrics = {
            "revenue": "Revenue (CHF m)",
            "ebitda": "EBITDA (CHF m)",
            "ebit": "EBIT (CHF m)",
            "net_income": "Net Income (CHF m)",
            "free_cash_flow": "Free Cash Flow (CHF m)",
            "net_debt": "Net Debt (CHF m)",
            "total_debt": "Total Debt (CHF m)",
        }

        any_chart = False
        for col, label in fin_metrics.items():
            if col in ticker_fin.columns and ticker_fin[col].notna().any():
                fig = line_chart(ticker_fin, "fiscal_year", col, label, yaxis_label=label)
                st.plotly_chart(fig, use_container_width=True)
                any_chart = True
            else:
                st.caption(f"_{label}: no data available for this company._")
        if not any_chart:
            st.info("No financial metrics available for this company.")

# ── Tab 2: Ratios ─────────────────────────────────────────────────────────────
with tab2:
    st.markdown(f"### Ratio Trends — {selected_label}")
    if rat_df.empty:
        st.warning("Ratios not available.")
    else:
        ticker_rat = rat_df[rat_df["ticker"] == selected_ticker].sort_values("fiscal_year")

        ratio_metrics = {
            "roe": "Return on Equity (%)",
            "ebit_margin": "EBIT Margin (%)",
            "net_margin": "Net Margin (%)",
            "debt_to_equity": "Debt / Equity",
        }

        any_chart = False
        for col, label in ratio_metrics.items():
            if col in ticker_rat.columns and ticker_rat[col].notna().any():
                fig = line_chart(ticker_rat, "fiscal_year", col, label, yaxis_label=label)
                st.plotly_chart(fig, use_container_width=True)
                any_chart = True
            else:
                st.caption(f"_{label}: no data available for this company._")
        if not any_chart:
            st.info("No ratio metrics available for this company.")

# ── Tab 3: Beta Universe Comparison ──────────────────────────────────────────
with tab3:
    st.markdown("### Beta Universe Comparison")
    st.caption(
        "Comparison of the latest available year per company across the selected public beta universe. "
        "This is a beta universe comparison, not a sector median."
    )

    if rat_df.empty:
        st.warning("Ratios not available.")
    else:
        # Comparison company selector
        comp_btn1, comp_btn2, _ = st.columns([1, 1, 6])
        if comp_btn1.button("Select all companies", key="comp_sel_all"):
            st.session_state["comparison_select"] = all_labels
        if comp_btn2.button("Clear comparison", key="comp_clear"):
            st.session_state["comparison_select"] = []

        if "comparison_select" not in st.session_state:
            st.session_state["comparison_select"] = all_labels

        comparison_labels = st.multiselect(
            "Companies to compare",
            options=all_labels,
            default=st.session_state.get("comparison_select", all_labels),
            key="comparison_select",
        )
        st.caption("Choose the companies included in the beta universe comparison.")

        comparison_tickers = [label_to_ticker[l] for l in comparison_labels if l in label_to_ticker]

        if not comparison_tickers:
            st.warning("Select at least one company to display comparison charts.")
        else:
            latest_year_per_ticker = (
                rat_df.groupby("ticker")["fiscal_year"].max()
                .reset_index()
                .rename(columns={"fiscal_year": "latest_year"})
            )
            latest_rat = rat_df.merge(latest_year_per_ticker, on="ticker")
            latest_rat = latest_rat[
                (latest_rat["fiscal_year"] == latest_rat["latest_year"]) &
                (latest_rat["ticker"].isin(comparison_tickers))
            ]

            universe_metrics = {
                "roe": "Return on Equity (%)",
                "ebit_margin": "EBIT Margin (%)",
                "net_margin": "Net Margin (%)",
                "debt_to_equity": "Debt / Equity",
                "ev_to_ebitda": "EV / EBITDA",
                "pe_ratio": "P/E Ratio",
            }

            if latest_rat.empty:
                st.info("No data available for the selected companies.")
            else:
                chart_cols = st.columns(2)
                col_idx = 0
                for metric, label in universe_metrics.items():
                    if metric in latest_rat.columns and latest_rat[metric].notna().any():
                        fig = beta_universe_bar(latest_rat, metric, f"{label} — Latest Year")
                        chart_cols[col_idx % 2].plotly_chart(fig, use_container_width=True)
                        col_idx += 1
                    else:
                        st.caption(f"_{label}: not available across the selected companies._")

# ── Tab 4: Analytical Flags ───────────────────────────────────────────────────
with tab4:
    st.markdown("### Analytical Flags")
    st.info(
        "These flags are rule-based indicators designed to highlight accounting, data quality or trend patterns. "
        "They are not investment recommendations.",
        icon="ℹ️",
    )

    flag_rows = []

    if not fin_df.empty:
        for _, row in fin_df.iterrows():
            t = str(row.get("ticker", ""))
            fy = row.get("fiscal_year", "")
            co = row.get("company_name", "")

            fcf = row.get("free_cash_flow")
            if pd.notna(fcf) and fcf < 0:
                flag_rows.append({"ticker": t, "company": co, "fiscal_year": fy, "flag": "Negative free cash flow", "severity": "warning"})

            ebit = row.get("ebit")
            revenue = row.get("revenue")
            if pd.notna(ebit) and pd.notna(revenue) and revenue != 0:
                if (ebit / revenue * 100) < 5:
                    flag_rows.append({"ticker": t, "company": co, "fiscal_year": fy, "flag": "EBIT margin below 5%", "severity": "warning"})

            missing = [f for f in ["revenue", "ebit", "net_income"] if pd.isna(row.get(f))]
            if missing:
                flag_rows.append({"ticker": t, "company": co, "fiscal_year": fy, "flag": f"Missing key fields: {', '.join(missing)}", "severity": "info"})

    if not rat_df.empty:
        for _, row in rat_df.iterrows():
            t = str(row.get("ticker", ""))
            fy = row.get("fiscal_year", "")
            co = row.get("company_name", "")

            roe = row.get("roe")
            if pd.notna(roe) and roe < 5:
                flag_rows.append({"ticker": t, "company": co, "fiscal_year": fy, "flag": "ROE below 5%", "severity": "warning"})

            dte = row.get("debt_to_equity")
            if pd.notna(dte) and dte > 2:
                flag_rows.append({"ticker": t, "company": co, "fiscal_year": fy, "flag": "Debt/Equity above 2", "severity": "warning"})

            if "per_share_not_comparable_pre_split" in str(row.get("quality_notes", "")):
                flag_rows.append({"ticker": t, "company": co, "fiscal_year": fy, "flag": "Per-share data not comparable pre-split", "severity": "info"})

    if flag_rows:
        flags_df = pd.DataFrame(flag_rows).sort_values(["ticker", "fiscal_year"])

        col_f1, col_f2 = st.columns(2)
        filter_tickers = col_f1.multiselect(
            "Filter by Ticker",
            options=sorted(flags_df["ticker"].unique()),
            default=sorted(flags_df["ticker"].unique()),
        )
        filter_severity = col_f2.multiselect(
            "Filter by Severity",
            options=sorted(flags_df["severity"].unique()),
            default=sorted(flags_df["severity"].unique()),
        )

        filtered_flags = flags_df[
            flags_df["ticker"].isin(filter_tickers) & flags_df["severity"].isin(filter_severity)
        ]
        st.dataframe(filtered_flags, use_container_width=True, hide_index=True)
        st.caption(f"{len(filtered_flags)} flags shown.")
    else:
        st.success("No analytical flags generated for the loaded data.")

st.divider()
st.warning(
    "**Disclaimer:** This app is for analysis support only. "
    "It does not provide investment advice, buy/sell recommendations, stock picks or price predictions."
)
