from __future__ import annotations

import pandas as pd

from src.data.semantic import leave_exclusion_mask, month_key_to_period


def capacity_pack(df: pd.DataFrame, group_keys: list[str], weeks_in_window: int) -> pd.DataFrame:
    df = df.copy()
    df = df.loc[~leave_exclusion_mask(df)]

    staff = df.groupby(group_keys, dropna=False).agg(
        utilisation_target=("utilisation_target", "mean"),
        fte_hours_scaling=("fte_hours_scaling", "mean"),
    )
    staff["weekly_capacity"] = 38 * staff["fte_hours_scaling"]
    staff["period_capacity"] = staff["weekly_capacity"] * weeks_in_window
    staff["billable_capacity"] = staff["period_capacity"] * staff["utilisation_target"]

    periods = month_key_to_period(df["month_key"])
    df["month_period"] = periods
    latest = periods.max()
    if latest is pd.NaT:
        trailing = df.iloc[0:0]
    else:
        cutoff = latest - 1
        trailing = df.loc[periods >= cutoff]

    trailing_billable = trailing.loc[trailing["is_billable"]].groupby(group_keys, dropna=False)["hours_raw"].sum()
    trailing_total = trailing.groupby(group_keys, dropna=False)["hours_raw"].sum()

    staff["trailing_billable_load"] = trailing_billable
    staff["trailing_total_load"] = trailing_total
    staff = staff.fillna({"trailing_billable_load": 0, "trailing_total_load": 0})
    staff["headroom"] = staff["billable_capacity"] - staff["trailing_billable_load"]

    return staff.reset_index()
