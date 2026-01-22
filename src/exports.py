from __future__ import annotations

import io
import json
from typing import Any

import pandas as pd
import streamlit as st


def export_csv(df: pd.DataFrame, filename: str, label: str) -> None:
    csv_data = df.to_csv(index=False).encode("utf-8")
    st.download_button(label, data=csv_data, file_name=filename, mime="text/csv")


def export_json(data: Any, filename: str, label: str) -> None:
    payload = json.dumps(data, indent=2)
    st.download_button(label, data=payload, file_name=filename, mime="application/json")


def export_dataframe_bytes(df: pd.DataFrame) -> bytes:
    buffer = io.StringIO()
    df.to_csv(buffer, index=False)
    return buffer.getvalue().encode("utf-8")
