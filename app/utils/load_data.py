from pathlib import Path
import pandas as pd
import streamlit as st

DATA_DIR = Path(__file__).resolve().parents[2] / "beta_product_data"
EXPORT_PATH = Path(__file__).resolve().parents[2] / "exports" / "swiss_equity_data_public_beta.xlsx"


@st.cache_data
def _read_csv_cached(filename: str, modified_ns: int) -> pd.DataFrame:
    path = DATA_DIR / filename
    return pd.read_csv(path)


def _safe_read(filename: str) -> pd.DataFrame:
    path = DATA_DIR / filename
    if not path.exists():
        st.error(f"Data file not found: beta_product_data/{filename}. Please ensure the repository is complete.")
        return pd.DataFrame()
    return _read_csv_cached(filename, path.stat().st_mtime_ns)


def load_financials() -> pd.DataFrame:
    return _safe_read("financials.csv")


def load_ratios() -> pd.DataFrame:
    return _safe_read("ratios.csv")


def load_quality() -> pd.DataFrame:
    return _safe_read("data_quality_report.csv")


def load_quality_summary() -> pd.DataFrame:
    return _safe_read("data_quality_summary.csv")


def load_companies() -> pd.DataFrame:
    return _safe_read("company_master.csv")


def load_dictionary() -> pd.DataFrame:
    return _safe_read("data_dictionary.csv")


def load_sources() -> pd.DataFrame:
    return _safe_read("sources.csv")


def load_all_data() -> dict:
    return {
        "financials": load_financials(),
        "ratios": load_ratios(),
        "quality": load_quality(),
        "companies": load_companies(),
        "dictionary": load_dictionary(),
        "sources": load_sources(),
    }
