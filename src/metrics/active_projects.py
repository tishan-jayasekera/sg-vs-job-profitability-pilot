from __future__ import annotations

import pandas as pd

from src.data.job_lifecycle import active_jobs
from src.data.semantic import safe_quote_rollup, rate_rollups, scope_creep


def active_projects_pack(df: pd.DataFrame, recency_days: int) -> pd.DataFrame:
    active_df = active_jobs(df, recency_days)
    group_keys = ["job_no", "department_final", "job_category"]
    quote = safe_quote_rollup(active_df, group_keys)
    actual = active_df.groupby(group_keys, dropna=False).agg(
        actual_hours=("hours_raw", "sum"),
        revenue=("rev_alloc", "sum"),
    )
    creep_hours = active_df.loc[scope_creep(active_df)].groupby(group_keys, dropna=False)["hours_raw"].sum()

    merged = actual.join(quote.set_index(group_keys), how="left")
    merged["quote_consumed_pct"] = merged["actual_hours"] / merged["quoted_hours"].replace({0: pd.NA})
    merged["scope_creep_hours"] = creep_hours
    merged["scope_creep_share"] = merged["scope_creep_hours"] / merged["actual_hours"].replace({0: pd.NA})

    rates = rate_rollups(active_df, group_keys)
    merged = merged.reset_index().merge(rates, on=group_keys, how="left")
    merged["rate_variance"] = merged["realised_rate"] - merged["quote_rate"]

    if "job_due_date" in active_df.columns:
        due_dates = active_df.groupby(group_keys, dropna=False)["job_due_date"].min().reset_index()
        merged = merged.merge(due_dates, on=group_keys, how="left")
    if "client" in active_df.columns:
        clients = active_df.groupby(group_keys, dropna=False)["client"].first().reset_index()
        merged = merged.merge(clients, on=group_keys, how="left")

    return merged
