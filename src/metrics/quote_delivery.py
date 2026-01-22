from __future__ import annotations

import pandas as pd

from src.data.semantic import safe_quote_rollup, safe_quote_job_task, scope_creep


def quote_delivery_pack(df: pd.DataFrame, group_keys: list[str], severe_overrun_multiplier: float = 1.2) -> pd.DataFrame:
    quote_rollup = safe_quote_rollup(df, group_keys)
    actuals = (
        df.groupby(group_keys, dropna=False)
        .agg(hours=("hours_raw", "sum"))
        .reset_index()
    )
    merged = actuals.merge(quote_rollup, on=group_keys, how="left")
    merged["hours_variance"] = merged["hours"] - merged["quoted_hours"]
    merged["hours_variance_pct"] = merged["hours_variance"] / merged["quoted_hours"].replace({0: pd.NA})

    creep_mask = scope_creep(df)
    creep_hours = df.loc[creep_mask].groupby(group_keys, dropna=False)["hours_raw"].sum()
    merged["unquoted_hours"] = merged.set_index(group_keys).index.map(creep_hours).fillna(0).values
    merged["unquoted_share"] = merged["unquoted_hours"] / merged["hours"].replace({0: pd.NA})

    job_task = safe_quote_job_task(df)
    job_task_actual = df.groupby(["job_no", "task_name"], dropna=False)["hours_raw"].sum().reset_index()
    job_task = job_task.merge(job_task_actual, on=["job_no", "task_name"], how="left")
    job_task["overrun"] = job_task["hours_raw"] > job_task["quoted_time_total"].fillna(0)
    job_task["severe_overrun"] = job_task["hours_raw"] > job_task["quoted_time_total"].fillna(0) * severe_overrun_multiplier

    overrun_rate = job_task.groupby(group_keys, dropna=False)["overrun"].mean()
    severe_rate = job_task.groupby(group_keys, dropna=False)["severe_overrun"].mean()
    merged["overrun_rate"] = merged.set_index(group_keys).index.map(overrun_rate).values
    merged["severe_overrun_rate"] = merged.set_index(group_keys).index.map(severe_rate).values

    return merged
