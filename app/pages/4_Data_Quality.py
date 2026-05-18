import streamlit as st
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from utils.load_data import load_quality, load_quality_summary, load_sources, load_companies, load_field_provenance

st.set_page_config(page_title="Data Quality — Swiss Equity Data", layout="wide")

# ── Language selector ──────────────────────────────────────────────────────────
lang = st.radio("Language / Langue", ["EN", "FR"], horizontal=True, label_visibility="collapsed")

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 0 — Data Quality & Sources explanation
# ══════════════════════════════════════════════════════════════════════════════
if lang == "EN":
    st.title("Data Quality and Sources")
    st.markdown(
        """
Swiss Equity Data is built from company-reported annual information and structured into a
consistent format for analysis. The dataset includes source tracking, quality notes and
documented limitations so users can understand where the numbers come from and which fields
require caution.
"""
    )
    st.markdown(
        """
- Annual reports and company disclosures are used as validation sources where available.
- Financial fields are normalized into a consistent structure.
- Some values are reported directly by companies, while others may be calculated from reported figures.
- Missing fields are documented instead of being filled with invented values.
- Quality notes explain caveats such as unavailable fields, calculated metrics, restatements, split effects or company-specific reporting conventions.
- The beta is designed for analysis support, not investment advice.
"""
    )
else:
    st.title("Qualité des données et sources")
    st.markdown(
        """
Swiss Equity Data est construit à partir d'informations annuelles publiées par les sociétés
et structurées dans un format cohérent pour l'analyse. Le dataset inclut le suivi des sources,
des notes qualité et des limites documentées afin que l'utilisateur comprenne d'où viennent
les chiffres et quels champs doivent être traités avec prudence.
"""
    )
    st.markdown(
        """
- Les rapports annuels et publications des sociétés sont utilisés comme sources de validation lorsque disponibles.
- Les champs financiers sont normalisés dans une structure cohérente.
- Certaines valeurs sont reportées directement par les sociétés, tandis que d'autres peuvent être calculées à partir de chiffres publiés.
- Les champs manquants sont documentés au lieu d'être remplacés par des valeurs inventées.
- Les notes qualité expliquent les limites : champs indisponibles, métriques calculées, retraitements, effets de splits ou conventions propres à certaines sociétés.
- La beta sert de support d'analyse, pas de conseil en investissement.
"""
    )

st.divider()

if lang == "EN":
    st.markdown(
        """
This page summarizes the quality checks applied to the public beta dataset.
Notes are classified by severity so methodological notes, acceptable limitations
and review items are clearly separated.
"""
    )
else:
    st.markdown(
        """
Cette page résume les contrôles qualité appliqués au dataset public beta.
Les notes sont classées par sévérité afin de distinguer les notes méthodologiques,
les limites acceptables et les éléments à vérifier.
"""
    )

st.info(
    "Future versions are expected to expand field-level provenance tracking and source reconciliation coverage."
    if lang == "EN"
    else
    "Les versions futures devraient étendre le suivi de la provenance par champ et la couverture de réconciliation des sources."
)

# ── Load data ──────────────────────────────────────────────────────────────────
summary_df      = load_quality_summary()
report_df       = load_quality()
sources_df      = load_sources()
companies_df    = load_companies()
provenance_df   = load_field_provenance()

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

ticker_to_label, label_to_ticker = build_label_maps(summary_df, report_df, companies_df, sources_df)

def ticker_label(t: str) -> str:
    return ticker_to_label.get(str(t), str(t))


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — Top KPIs from summary
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("### Quality at a Glance")

if summary_df.empty:
    st.warning("Quality summary data not available.")
else:
    status_col = "overall_quality_status" if "overall_quality_status" in summary_df.columns else None

    obs_total = len(summary_df)
    if status_col:
        normalized_status = summary_df[status_col].fillna("").astype(str).str.strip()
        high_conf = int((normalized_status == "High confidence").sum())
        usable_notes = int((normalized_status == "Usable with notes").sum())
        needs_review = int((normalized_status == "Needs review").sum())
        critical_issues = int(normalized_status.str.startswith("Critical").sum())
    else:
        high_conf = usable_notes = needs_review = critical_issues = "—"

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Company-year observations", obs_total)
    k2.metric("High confidence",           high_conf)
    k3.metric("Usable with notes",         usable_notes)
    k4.metric("Needs review",              needs_review)
    k5.metric("Critical issues",           critical_issues)

    if critical_issues == 0 or critical_issues == "—":
        st.success("No critical issues detected in the current public beta dataset.")

st.divider()


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — Severity breakdown from report
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("### Severity Breakdown")
st.caption("Based on detailed notes from data_quality_report.csv.")

if not report_df.empty and "severity" in report_df.columns:
    sev_order = ["INFO", "WARNING", "REVIEW", "CRITICAL"]
    sev_counts = report_df["severity"].fillna("").astype(str).str.strip().str.upper().value_counts()

    sev_cols = st.columns(4)
    for i, key in enumerate(sev_order):
        count = int(sev_counts.get(key, 0))
        sev_cols[i].metric(key, count)
else:
    st.caption("Severity data not available.")

with st.expander("Severity level reference"):
    st.markdown(
        """
| Severity | Meaning |
|----------|---------|
| **INFO** | Methodological note — informational context, not an error |
| **WARNING** | A value or field warrants awareness before use |
| **REVIEW** | The value or context should be verified before detailed analysis |
| **CRITICAL** | A significant data issue that may affect usability |
        """
    )

st.divider()


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3 — Quality summary table (company-year level)
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("### Quality Summary by Company-Year")
st.caption("One row per company and fiscal year, showing aggregated quality status.")

if summary_df.empty:
    st.warning("Quality summary not available.")
else:
    sf1, sf2, sf3 = st.columns(3)

    # Company filter
    with sf1:
        if "ticker" in summary_df.columns:
            sum_tickers = sorted(summary_df["ticker"].dropna().unique().tolist())
            sum_labels  = sorted(ticker_label(t) for t in sum_tickers)
            sum_l2t     = {ticker_label(t): t for t in sum_tickers}
            sel_sum_labels = st.multiselect(
                "Ticker", options=sum_labels, default=sum_labels, key="sum_ticker",
                help="Search by ticker or company name.",
            )
            sel_sum_tickers = [sum_l2t[l] for l in sel_sum_labels if l in sum_l2t]
        else:
            sel_sum_tickers = []

    # Fiscal year filter
    with sf2:
        if "fiscal_year" in summary_df.columns:
            sum_years = sorted(summary_df["fiscal_year"].dropna().unique().tolist())
            sel_sum_years = st.multiselect("Fiscal year", options=sum_years, default=sum_years, key="sum_year")
        else:
            sel_sum_years = None

    # Status filter
    with sf3:
        if status_col:
            statuses = sorted(summary_df[status_col].dropna().unique().tolist())
            sel_statuses = st.multiselect("Overall quality status", options=statuses, default=statuses, key="sum_status")
        else:
            sel_statuses = None

    # Apply filters
    filtered_sum = summary_df.copy()
    if sel_sum_tickers and "ticker" in filtered_sum.columns:
        filtered_sum = filtered_sum[filtered_sum["ticker"].isin(sel_sum_tickers)]
    if sel_sum_years and "fiscal_year" in filtered_sum.columns:
        filtered_sum = filtered_sum[filtered_sum["fiscal_year"].isin(sel_sum_years)]
    if sel_statuses and status_col:
        filtered_sum = filtered_sum[filtered_sum[status_col].isin(sel_statuses)]

    sum_display_cols = [c for c in [
        "ticker", "company_name", "sector", "fiscal_year",
        "info_count", "warning_count", "review_count", "critical_count",
        "total_flags", "overall_quality_status", "public_summary",
    ] if c in filtered_sum.columns]

    if filtered_sum.empty:
        st.info("No rows match the current filters.")
    else:
        st.dataframe(filtered_sum[sum_display_cols], use_container_width=True, hide_index=True)
        st.caption(f"{len(filtered_sum):,} company-year rows shown.")

st.divider()


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4 — Detailed notes from report
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("### Detailed Quality Notes")
st.caption("Individual documented notes from the quality report, one row per issue.")

if report_df.empty:
    st.warning("Detailed quality report not available.")
else:
    rf1, rf2, rf3, rf4, rf5 = st.columns(5)

    # Company filter
    with rf1:
        if "ticker" in report_df.columns:
            rep_tickers = sorted(report_df["ticker"].dropna().unique().tolist())
            rep_labels  = sorted(ticker_label(t) for t in rep_tickers)
            rep_l2t     = {ticker_label(t): t for t in rep_tickers}
            sel_rep_labels = st.multiselect(
                "Ticker", options=rep_labels, default=rep_labels, key="rep_ticker",
                help="Search by ticker or company name.",
            )
            sel_rep_tickers = [rep_l2t[l] for l in sel_rep_labels if l in rep_l2t]
        else:
            sel_rep_tickers = []

    # Fiscal year filter
    with rf2:
        if "fiscal_year" in report_df.columns:
            rep_years = sorted(report_df["fiscal_year"].dropna().unique().tolist())
            sel_rep_years = st.multiselect("Fiscal year", options=rep_years, default=rep_years, key="rep_year")
        else:
            sel_rep_years = None

    # Severity filter (raw uppercase values from CSV)
    with rf3:
        if "severity" in report_df.columns:
            severities = sorted(report_df["severity"].dropna().unique().tolist())
            sel_severities = st.multiselect("Severity", options=severities, default=severities, key="rep_sev")
        else:
            sel_severities = None

    # Public label filter
    with rf4:
        if "public_label" in report_df.columns:
            pub_labels = sorted(report_df["public_label"].dropna().unique().tolist())
            sel_pub_labels = st.multiselect(
                "Public label", options=pub_labels, default=pub_labels, key="rep_label",
            )
        else:
            sel_pub_labels = None

    # Issue type filter
    with rf5:
        if "issue_type" in report_df.columns:
            issue_types = sorted(report_df["issue_type"].dropna().unique().tolist())
            sel_issue_types = st.multiselect(
                "Issue type", options=issue_types, default=issue_types, key="rep_issue_type",
            )
        else:
            sel_issue_types = None

    # Apply filters
    if not sel_rep_tickers and "ticker" in report_df.columns:
        st.info("No companies selected. Select at least one company to display notes.")
    else:
        filtered_rep = report_df.copy()
        if sel_rep_tickers and "ticker" in filtered_rep.columns:
            filtered_rep = filtered_rep[filtered_rep["ticker"].isin(sel_rep_tickers)]
        if sel_rep_years and "fiscal_year" in filtered_rep.columns:
            filtered_rep = filtered_rep[filtered_rep["fiscal_year"].isin(sel_rep_years)]
        if sel_severities and "severity" in filtered_rep.columns:
            filtered_rep = filtered_rep[filtered_rep["severity"].isin(sel_severities)]
        if sel_pub_labels and "public_label" in filtered_rep.columns:
            filtered_rep = filtered_rep[filtered_rep["public_label"].isin(sel_pub_labels)]
        if sel_issue_types and "issue_type" in filtered_rep.columns:
            filtered_rep = filtered_rep[filtered_rep["issue_type"].isin(sel_issue_types)]

        rep_display_cols = [c for c in [
            "ticker", "company_name", "sector", "fiscal_year",
            "severity", "public_label", "issue_type", "column", "value", "public_note",
        ] if c in filtered_rep.columns]

        if filtered_rep.empty:
            st.info("No notes match the current filters.")
        else:
            st.dataframe(filtered_rep[rep_display_cols], use_container_width=True, hide_index=True)
            st.caption(f"{len(filtered_rep):,} documented notes shown.")

st.divider()


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 5 — Source coverage
# ══════════════════════════════════════════════════════════════════════════════
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

    src_rows      = len(source_display)
    src_companies = source_display["ticker"].nunique() if "ticker" in source_display.columns else "—"
    if "source_url" in source_display.columns:
        src_urls_available = int(source_display["source_url"].notna().sum())
        src_urls_missing   = int(source_display["source_url"].isna().sum())
    else:
        src_urls_available = "—"
        src_urls_missing   = "—"

    sc1, sc2, sc3, sc4 = st.columns(4)
    sc1.metric("Source records",        src_rows)
    sc2.metric("Companies covered",     src_companies)
    sc3.metric("Source URLs available", src_urls_available)
    sc4.metric("Source URLs pending",   src_urls_missing)

    st.dataframe(source_display, use_container_width=True, hide_index=True)

st.divider()


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 6 — Quality status guide
# ══════════════════════════════════════════════════════════════════════════════
if lang == "EN":
    st.markdown("### How to read our data quality statuses")
    with st.expander("Expand status definitions", expanded=False):
        st.markdown(
            """
The beta dataset assigns one of four quality statuses to field-level provenance records.
These statuses describe how each value was obtained and what care is needed when using it.

| Status | Meaning |
|--------|---------|
| ✅ **Verified** | The value is available and has been checked against the source information for that company and fiscal year. |
| 🔵 **Calculated** | The value was calculated by Swiss Equity Data from available inputs using a documented formula — for example, free cash flow = operating cash flow minus capital expenditures. |
| ⚠️ **Usable with notes** | The value is present but carries a caveat around source labelling, definition, unit, comparability across years, or review status. Read the provenance notes before using this value in analysis. |
| ❌ **Documented missing** | The value has been intentionally left blank because the required input is unavailable, has not been extracted yet, or cannot be derived safely from the available data. |

**Missing values are documented rather than invented.** When a field cannot be reliably populated,
it is left empty and the reason is recorded in the provenance notes.

---

*Not all fields in the dataset carry a provenance record.
Field-level provenance is currently available for selected fields only
(revenue, EBITDA, net income, EPS, free cash flow) and covers fiscal years 2023–2024.
Fields without a provenance record are displayed normally without a badge.*
"""
        )
else:
    st.markdown("### Comment lire nos statuts de qualité")
    with st.expander("Afficher les définitions des statuts", expanded=False):
        st.markdown(
            """
Le dataset beta assigne l'un de quatre statuts de qualité aux enregistrements de provenance par champ.
Ces statuts décrivent comment chaque valeur a été obtenue et quelle précaution est nécessaire lors de son utilisation.

| Statut | Signification |
|--------|---------------|
| ✅ **Vérifié** | La valeur est disponible et a été vérifiée par rapport aux informations sources disponibles pour cette société et cet exercice fiscal. |
| 🔵 **Calculé** | La valeur a été calculée par Swiss Equity Data à partir des données disponibles, selon une formule documentée — par exemple, flux de trésorerie libre = flux de trésorerie opérationnel moins les dépenses d'investissement. |
| ⚠️ **Utilisable avec notes** | La valeur est présente mais comporte une réserve concernant le libellé de la source, la définition, l'unité, la comparabilité entre exercices ou le statut de révision. Lisez les notes de provenance avant d'utiliser cette valeur dans une analyse. |
| ❌ **Manquante documentée** | La valeur a été intentionnellement laissée vide car la donnée requise est indisponible, n'a pas encore été extraite, ou ne peut pas être dérivée en toute sécurité à partir des données disponibles. |

**Les valeurs manquantes sont documentées, non inventées.** Lorsqu'un champ ne peut pas être
renseigné de manière fiable, il est laissé vide et la raison est consignée dans les notes de provenance.

---

*Tous les champs du dataset ne disposent pas d'un enregistrement de provenance.
La provenance par champ est actuellement disponible pour des champs sélectionnés uniquement
(chiffre d'affaires, EBITDA, résultat net, BPA, flux de trésorerie libre) et couvre les exercices 2023–2024.
Les champs sans enregistrement de provenance sont affichés normalement sans badge.*
"""
        )

st.divider()


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 7 — Field-level provenance preview
# ══════════════════════════════════════════════════════════════════════════════
if lang == "EN":
    st.markdown("### Field-level Provenance Preview")
    st.info(
        "**Beta preview — source tracking per field.** "
        "This section shows the source document, page reference, calculation method and quality status "
        "for individual data fields. "
        "Provenance is currently available for selected fields only (revenue, EBITDA, net income, EPS, free cash flow) "
        "and covers fiscal years 2023–2024. "
        "Coverage will be expanded in future versions of the dataset.",
        icon="🔍",
    )
else:
    st.markdown("### Aperçu de la provenance par champ")
    st.info(
        "**Aperçu beta — suivi des sources par champ.** "
        "Cette section indique le document source, la référence de page, la méthode de calcul et le statut qualité "
        "pour chaque champ de données individuellement. "
        "La provenance est actuellement disponible pour des champs sélectionnés uniquement "
        "(chiffre d'affaires, EBITDA, résultat net, BPA, flux de trésorerie libre) "
        "et couvre les exercices 2023–2024. "
        "La couverture sera étendue dans les versions futures du dataset.",
        icon="🔍",
    )

if provenance_df.empty:
    st.warning(
        "Field provenance data not available."
        if lang == "EN"
        else "Données de provenance par champ non disponibles."
    )
else:
    pf1, pf2, pf3, pf4 = st.columns(4)

    with pf1:
        prov_tickers = sorted(provenance_df["ticker"].dropna().unique().tolist())
        prov_labels  = sorted(ticker_label(t) for t in prov_tickers)
        prov_l2t     = {ticker_label(t): t for t in prov_tickers}
        sel_prov_labels = st.multiselect(
            "Ticker" if lang == "EN" else "Ticker",
            options=prov_labels,
            default=prov_labels,
            key="prov_ticker",
            help="Search by ticker or company name." if lang == "EN" else "Rechercher par ticker ou nom de société.",
        )
        sel_prov_tickers = [prov_l2t[l] for l in sel_prov_labels if l in prov_l2t]

    with pf2:
        prov_years = sorted(provenance_df["fiscal_year"].dropna().unique().tolist())
        sel_prov_years = st.multiselect(
            "Fiscal year" if lang == "EN" else "Exercice fiscal",
            options=prov_years,
            default=prov_years,
            key="prov_year",
        )

    with pf3:
        prov_fields = sorted(provenance_df["field_name"].dropna().unique().tolist())
        sel_prov_fields = st.multiselect(
            "Field" if lang == "EN" else "Champ",
            options=prov_fields,
            default=prov_fields,
            key="prov_field",
        )

    with pf4:
        prov_statuses = sorted(provenance_df["quality_status"].dropna().unique().tolist())
        sel_prov_statuses = st.multiselect(
            "Quality status" if lang == "EN" else "Statut qualité",
            options=prov_statuses,
            default=prov_statuses,
            key="prov_status",
        )

    filtered_prov = provenance_df.copy()
    if sel_prov_tickers:
        filtered_prov = filtered_prov[filtered_prov["ticker"].isin(sel_prov_tickers)]
    if sel_prov_years:
        filtered_prov = filtered_prov[filtered_prov["fiscal_year"].isin(sel_prov_years)]
    if sel_prov_fields:
        filtered_prov = filtered_prov[filtered_prov["field_name"].isin(sel_prov_fields)]
    if sel_prov_statuses:
        filtered_prov = filtered_prov[filtered_prov["quality_status"].isin(sel_prov_statuses)]

    prov_display_cols = [c for c in [
        "ticker", "fiscal_year", "field_name", "value",
        "source_name", "source_type", "source_url", "source_page", "source_label",
        "calculation_method", "quality_status", "notes",
    ] if c in filtered_prov.columns]

    if filtered_prov.empty:
        st.info(
            "No provenance records match the current filters."
            if lang == "EN"
            else "Aucun enregistrement de provenance ne correspond aux filtres actuels."
        )
    else:
        st.dataframe(filtered_prov[prov_display_cols], use_container_width=True, hide_index=True)
        st.caption(
            f"{len(filtered_prov):,} provenance record(s) shown — selected fields only. "
            "Financial values shown here are read-only and are not modified by this view."
            if lang == "EN"
            else
            f"{len(filtered_prov):,} enregistrement(s) de provenance affiché(s) — champs sélectionnés uniquement. "
            "Les valeurs financières affichées ici sont en lecture seule et ne sont pas modifiées par cet affichage."
        )

st.divider()
st.warning(
    "**Disclaimer:** This app is for analysis support only. "
    "It does not provide investment advice, buy/sell recommendations, stock picks or price predictions."
)
