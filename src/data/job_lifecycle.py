from __future__ import annotations

import pandas as pd

from src.data.semantic import month_key_to_period


def first_activity_month(df: pd.DataFrame) -> pd.DataFrame:
    periods = month_key_to_period(df["month_key"])
    df = df.copy()
    df["month_period"] = periods
    return df.groupby("job_no", dropna=False)["month_period"].min().reset_index()


def first_revenue_month(df: pd.DataFrame) -> pd.DataFrame:
    periods = month_key_to_period(df["month_key"])
    df = df.copy()
    df["month_period"] = periods
    revenue_month = df.loc[df["rev_alloc"] > 0]
    return revenue_month.groupby("job_no", dropna=False)["month_period"].min().reset_index()


def active_jobs(df: pd.DataFrame, recency_days: int) -> pd.DataFrame:
    df = df.copy()
    if "job_completed_date" in df.columns:
        not_completed = df["job_completed_date"].isna()
    elif "job_status" in df.columns:
        not_completed = ~df["job_status"].astype(str).str.lower().eq("completed")
    else:
        not_completed = pd.Series(True, index=df.index)

    if "date" in df.columns:
        latest = pd.to_datetime(df["date"], errors="coerce")
    elif "work_date" in df.columns:
        latest = pd.to_datetime(df["work_date"], errors="coerce")
    else:
        latest = pd.to_datetime(df["month_key"].astype(str).str[:7] + "-01", errors="coerce")

    recent_cutoff = latest.max() - pd.Timedelta(days=recency_days)
    recent = latest >= recent_cutoff

    return df.loc[not_completed & recent]
