from __future__ import annotations

import pandas as pd


def profitability_pack(df: pd.DataFrame, group_keys: list[str]) -> pd.DataFrame:
    grouped = df.groupby(group_keys, dropna=False).agg(
        hours=("hours_raw", "sum"),
        cost=("base_cost", "sum"),
        revenue=("rev_alloc", "sum"),
    )
    grouped["margin"] = grouped["revenue"] - grouped["cost"]
    grouped["margin_pct"] = grouped["margin"] / grouped["revenue"].replace({0: pd.NA})
    grouped["realised_rate"] = grouped["revenue"] / grouped["hours"].replace({0: pd.NA})
    return grouped.reset_index()
