from __future__ import annotations

import pandas as pd

from src.data.semantic import leave_exclusion_mask


def utilisation_pack(df: pd.DataFrame, group_keys: list[str], exclude_leave: bool = True) -> pd.DataFrame:
    df = df.copy()
    if exclude_leave:
        df = df.loc[~leave_exclusion_mask(df)]

    billable = df.loc[df["is_billable"]]
    billable_hours = billable.groupby(group_keys, dropna=False)["hours_raw"].sum()
    total_hours = df.groupby(group_keys, dropna=False)["hours_raw"].sum()

    util = pd.DataFrame({
        "billable_hours": billable_hours,
        "total_hours": total_hours,
    })
    util["utilisation"] = util["billable_hours"] / util["total_hours"].replace({0: pd.NA})

    target = df.groupby(group_keys, dropna=False).apply(
        lambda g: (g["utilisation_target"] * g["hours_raw"]).sum() / g["hours_raw"].sum()
        if g["hours_raw"].sum() else pd.NA
    )
    util["target"] = target
    util["util_gap"] = util["target"] - util["utilisation"]

    return util.reset_index()


def leakage_breakdown(df: pd.DataFrame, group_keys: list[str], breakdown_field: str = "breakdown") -> pd.DataFrame:
    df = df.copy()
    df = df.loc[~leave_exclusion_mask(df)]
    non_billable = df.loc[~df["is_billable"]]
    grouped = non_billable.groupby(group_keys + [breakdown_field], dropna=False)["hours_raw"].sum().reset_index()
    return grouped
