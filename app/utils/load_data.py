from pathlib import Path
import pandas as pd
import streamlit as st

DATA_DIR = Path(__file__).resolve().parents[2] / "beta_product_data"
EXPORT_PATH = Path(__file__).resolve().parents[2] / "exports" / "swiss_equity_data_public_beta.xlsx"


def _safe_read(filename: str) -> pd.DataFrame:
    path = DATA_DIR / filename
    if not path.exists():
        st.error(f"Data file not found: {path}. Please ensure the repository is complete.")
        return pd.DataFrame()
    return pd.read_csv(path)


@st.cache_data
def load_financials() -> pd.DataFrame:
    return _safe_read("financials.csv")


@st.cache_data
def load_ratios() -> pd.DataFrame:
    return _safe_read("ratios.csv")


@st.cache_data
def load_quality() -> pd.DataFrame:
    return _safe_read("data_quality_report.csv")


@st.cache_data
def load_quality_summary() -> pd.DataFrame:
    return _safe_read("data_quality_summary.csv")


@st.cache_data
def load_companies() -> pd.DataFrame:
    return _safe_read("company_master.csv")


@st.cache_data
def load_dictionary() -> pd.DataFrame:
    return _safe_read("data_dictionary.csv")


@st.cache_data
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
