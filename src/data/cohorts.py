from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional

import numpy as np
import pandas as pd

from src.data.semantic import month_key_to_period


@dataclass(frozen=True)
class CohortStats:
    n_jobs: int
    n_active_staff: int
    date_span: str
    recency_weighted: bool


def active_staff(df: pd.DataFrame, months: int) -> pd.Index:
    periods = month_key_to_period(df["month_key"])
    latest = periods.max()
    if latest is pd.NaT:
        return pd.Index([])
    cutoff = latest - months + 1
    recent = df.loc[periods >= cutoff]
    staff_hours = recent.groupby("staff_name")["hours_raw"].sum()
    return staff_hours[staff_hours > 0].index


def recency_weights(month_key: pd.Series, half_life_months: int) -> pd.Series:
    periods = month_key_to_period(month_key)
    latest = periods.max()
    if latest is pd.NaT:
        return pd.Series(1.0, index=month_key.index)
    months_diff = (latest - periods).astype(int)
    decay = 0.5 ** (months_diff / max(half_life_months, 1))
    return pd.Series(decay, index=month_key.index)


def weighted_median(series: pd.Series, weights: pd.Series) -> float:
    mask = series.notna() & weights.notna()
    if mask.sum() == 0:
        return float("nan")
    s = series[mask].astype(float)
    w = weights[mask].astype(float)
    order = np.argsort(s)
    s_sorted = s.iloc[order]
    w_sorted = w.iloc[order]
    cum = w_sorted.cumsum()
    cutoff = w_sorted.sum() * 0.5
    return float(s_sorted.iloc[cum.searchsorted(cutoff)])


def cohort_stats(df: pd.DataFrame, recency_weighted: bool, active_staff_months: int) -> CohortStats:
    periods = month_key_to_period(df["month_key"])
    date_span = "-"
    if periods.notna().any():
        date_span = f"{periods.min().strftime('%Y-%m')} to {periods.max().strftime('%Y-%m')}"
    staff_index = active_staff(df, active_staff_months)
    n_active_staff = int(len(staff_index))
    n_jobs = int(df["job_no"].nunique()) if "job_no" in df.columns else 0
    return CohortStats(n_jobs=n_jobs, n_active_staff=n_active_staff, date_span=date_span, recency_weighted=recency_weighted)
