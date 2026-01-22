from __future__ import annotations

import pandas as pd


def fmt_currency(value: float | int | pd.Series) -> str:
    if value is None or pd.isna(value):
        return "-"
    return f"${value:,.0f}"


def fmt_hours(value: float | int | pd.Series) -> str:
    if value is None or pd.isna(value):
        return "-"
    return f"{value:,.1f}"


def fmt_percent(value: float | int | pd.Series) -> str:
    if value is None or pd.isna(value):
        return "-"
    return f"{value:.1%}"


def fmt_rate(value: float | int | pd.Series) -> str:
    if value is None or pd.isna(value):
        return "-"
    return f"${value:,.0f}/hr"
