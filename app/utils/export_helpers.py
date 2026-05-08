from pathlib import Path
import pandas as pd

EXPORT_PATH = Path(__file__).resolve().parents[2] / "exports" / "swiss_equity_data_public_beta.xlsx"


def read_excel_bytes() -> bytes | None:
    if not EXPORT_PATH.exists():
        return None
    return EXPORT_PATH.read_bytes()


def dataframe_to_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")
