from __future__ import annotations

import pandas as pd

from src.data.job_lifecycle import first_activity_month, first_revenue_month
from src.data.semantic import month_key_to_period, safe_quote_job_task


def _job_level_quotes(df: pd.DataFrame) -> pd.DataFrame:
    job_task = safe_quote_job_task(df)
    job_quote = job_task.groupby("job_no", dropna=False).agg(
        quoted_hours=("quoted_time_total", "sum"),
        quoted_amount=("quoted_amount_total", "sum"),
    )
    return job_quote.reset_index()


def job_mix_pack(df: pd.DataFrame, capacity_df: pd.DataFrame, weeks_in_window: int, util_target: float) -> pd.DataFrame:
    df = df.copy()
    periods = month_key_to_period(df["month_key"])
    df["month_period"] = periods

    job_quote = _job_level_quotes(df)
    job_quote = job_quote.merge(first_activity_month(df), on="job_no", how="left", suffixes=("", "_activity"))
    job_quote = job_quote.merge(first_revenue_month(df), on="job_no", how="left", suffixes=("", "_revenue"))

    df_month = df.groupby(["month_key", "department_final", "job_category"], dropna=False).agg(
        job_count=("job_no", "nunique"),
    )
    quotes_month = df.groupby(["month_key", "department_final", "job_category"], dropna=False).apply(
        lambda g: pd.Series({
            "total_quoted_amount": job_quote.loc[job_quote["job_no"].isin(g["job_no"].unique()), "quoted_amount"].sum(),
            "total_quoted_hours": job_quote.loc[job_quote["job_no"].isin(g["job_no"].unique()), "quoted_hours"].sum(),
        })
    )
    mix = df_month.join(quotes_month)

    mix["avg_quoted_amount_per_job"] = mix["total_quoted_amount"] / mix["job_count"].replace({0: pd.NA})
    mix["avg_quoted_hours_per_job"] = mix["total_quoted_hours"] / mix["job_count"].replace({0: pd.NA})
    mix["value_per_quoted_hour"] = mix["total_quoted_amount"] / mix["total_quoted_hours"].replace({0: pd.NA})

    demand_hours = mix["total_quoted_hours"]
    capacity_supply = capacity_df["billable_capacity"].sum() if "billable_capacity" in capacity_df.columns else 0
    mix["implied_fte_required"] = demand_hours / (38 * weeks_in_window * util_target)
    mix["implied_utilisation"] = demand_hours / capacity_supply if capacity_supply else pd.NA
    mix["implied_slack"] = 1 - mix["implied_utilisation"]

    return mix.reset_index()
