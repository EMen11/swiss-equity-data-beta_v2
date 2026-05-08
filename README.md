# Swiss Equity Data — Public Beta

A Streamlit web application providing normalized annual fundamentals for selected Swiss listed companies, enriched with transparent data quality metadata, exportable datasets and a basic analytics layer.

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
| More Swiss listed companies | Planned |
| Broader SMI / SPI coverage | Planned |
| Python API | Planned (roadmap) |
| Exploratory MCP layer | Planned (roadmap) |
| Public source URL manifest | Planned |

**Python API:** A Python API is planned, but the current public beta is delivered through the Streamlit interface and exportable datasets.

**MCP Layer:** An exploratory MCP layer is planned to allow AI assistants and agent-based workflows to query verified Swiss equity fundamentals. This is designed for analysis support, not investment recommendations.

---

## Disclaimer

This is a public beta. Data is sourced from publicly available annual reports and may contain missing fields or quality flags. Content is provided for research and analysis support only. This is **not investment advice**, not stock picking, and not a buy/sell recommendation product.
