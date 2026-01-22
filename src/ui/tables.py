from __future__ import annotations

import pandas as pd
import streamlit as st


def drill_table(df: pd.DataFrame, key: str):
    return st.dataframe(df, use_container_width=True, key=key)


def ranked_table(df: pd.DataFrame, key: str, sort_col: str, top_n: int = 10):
    if sort_col in df.columns:
        df = df.sort_values(sort_col, ascending=False).head(top_n)
    return st.dataframe(df, use_container_width=True, key=key)
