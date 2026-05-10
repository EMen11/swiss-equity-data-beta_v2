# Swiss Equity Data — Public Beta

A Streamlit web application providing normalized annual fundamentals for selected Swiss listed companies, enriched with transparent data quality metadata, exportable datasets and a basic analytics layer.

This public beta is aligned with the v5.2 product direction: Annual Data Pack preview, controlled MCP / AI-ready access preview, and a PDF extractor / traceable validation pipeline roadmap.

---

## Current Beta Coverage

5 Swiss listed companies with up to 10 years of annual fundamentals:

| Ticker | Company | Sector |
|--------|---------|--------|
| DKSH.SW | DKSH Holding AG | Distribution / Services |
| HIAG.SW | HIAG Immobilien Holding AG | Real Estate |
| SCMN.SW | Swisscom AG | Telecom / Infrastructure |
| GEBN.SW | Geberit AG | Industrials / Building Products |
| SIKA.SW | Sika AG | Chemicals / Construction Materials |

---

## Features

- **Financials** — Normalized annual data: revenue, EBITDA, EBIT, net income, free cash flow, balance sheet items
- **Ratios** — ROE, EBIT margin, net margin, debt/equity, EV/EBITDA, P/E and more
- **Analytics** — Historical trend charts, beta universe comparison, rule-based analytical flags
- **Data Quality** — Per-field quality flags with severity levels and source manifest
- **Exports** — Full dataset as Excel (all sheets) and individual CSV files
- **Annual Data Pack Preview** — Excel and CSV downloads preview a future versioned, documented data pack
- **AI / MCP Preview** — Roadmap for controlled API/MCP access from Python and AI-assisted workflows

The current public beta remains a Streamlit app with Excel/CSV exports, reliability notes and basic analytics. MCP/API access is presented as a controlled access layer preview and roadmap item, not as an autonomous financial assistant.

---

## Data Files

```
beta_product_data/
├── financials.csv          Annual normalized financial data
├── ratios.csv              Calculated financial ratios and margins
├── data_quality_report.csv Per-field quality flags
├── company_master.csv      Company metadata and coverage
├── data_dictionary.csv     Field definitions and formulas
└── sources.csv             Source manifest per company and year

docs/
└── images/
    └── claude_mcp_demo.png Optional Claude Desktop MCP workflow screenshot

exports/
└── swiss_equity_data_public_beta.xlsx  Packaged Excel export (all sheets)
```

---

## How to Run Locally

```bash
pip install -r requirements.txt
streamlit run app/streamlit_app.py
```

The app will open at `http://localhost:8501`.

---

## Deploying to Streamlit Community Cloud

1. Push the repository to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io) and connect your repo.
3. Set the main file path to `app/streamlit_app.py`.
4. Deploy — no secrets or environment variables required.

---

## Roadmap

| Item | Status |
|------|--------|
| Streamlit public interface | Delivered (this beta) |
| 5 Swiss listed companies | Delivered (this beta) |
| Excel / CSV exports | Delivered (this beta) |
| Data quality metadata | Delivered (this beta) |
| Basic analytics layer | Delivered (this beta) |
| Annual Data Pack | Previewed by current Excel / CSV exports |
| FMP-based expansion | Planned |
| PDF extractor / traceable validation pipeline | Planned |
| Python API | Planned (roadmap) |
| Controlled MCP access | Planned (roadmap) |
| Public source URL manifest | Planned |

**Python API:** A Python API is planned, but the current public beta is delivered through the Streamlit interface and exportable datasets.

**Annual Data Pack:** The current Excel and CSV downloads are a small preview of a future versioned, documented dataset with financials, ratios, reliability notes, sources and methodology.

**MCP / AI-ready Access:** A controlled MCP/API access layer is planned to allow Claude, Cursor, Kimi and other AI-assisted workflows to query maintained Swiss equity data. It is designed for analysis support, deterministic calculations and export generation from structured data.

**PDF Extractor Roadmap:** Future versions are expected to use the PDF extractor as a traceable validation pipeline, including field-level provenance and reconciliation status between structured provider data and annual report extraction.

---

## Disclaimer

This is a public beta. Data is sourced from publicly available annual reports and may contain missing fields or quality flags. Content is provided for research and analysis support only. This is **not investment advice**, not stock picking, not price prediction, and not a buy/sell recommendation product.
