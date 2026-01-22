from __future__ import annotations

import pandas as pd

from src.data.semantic import safe_quote_rollup


def margin_bridge_pack(df: pd.DataFrame, group_keys: list[str]) -> pd.DataFrame:
    quote = safe_quote_rollup(df, group_keys)
    actual = df.groupby(group_keys, dropna=False).agg(
        actual_revenue=("rev_alloc", "sum"),
        actual_cost=("base_cost", "sum"),
        hours=("hours_raw", "sum"),
        billable_hours=("hours_raw", lambda s: s[df.loc[s.index, "is_billable"]].sum()),
    )
    actual["actual_margin"] = actual["actual_revenue"] - actual["actual_cost"]

    df = df.copy()
    df["cost_per_hour"] = df["base_cost"] / df["hours_raw"].replace({0: pd.NA})
    expected_cost_rate = df.groupby(group_keys, dropna=False)["cost_per_hour"].median()
    expected = quote.set_index(group_keys)
    expected_cost = expected["quoted_hours"] * expected_cost_rate
    expected_margin = expected["quoted_amount"] - expected_cost

    bridge = actual.copy()
    bridge = bridge.join(expected_cost_rate.rename("expected_cost_rate"), how="left")
    bridge = bridge.join(expected_cost.rename("expected_cost"), how="left")
    bridge = bridge.join(expected_margin.rename("expected_margin"), how="left")

    bridge["hours_variance_effect"] = (
        (bridge["hours"] - expected["quoted_hours"]) * bridge["expected_cost_rate"]
    )
    bridge["rate_variance_effect"] = bridge["actual_revenue"] - expected["quoted_amount"]
    bridge["cost_variance_effect"] = bridge["actual_cost"] - bridge["expected_cost"]

    billable_share = bridge["billable_hours"] / bridge["hours"].replace({0: pd.NA})
    bridge["non_billable_leakage_effect"] = (1 - billable_share.fillna(0)) * bridge["actual_cost"]

    bridge["total_variance"] = bridge["actual_margin"] - bridge["expected_margin"]
    for col in [
        "hours_variance_effect",
        "rate_variance_effect",
        "cost_variance_effect",
        "non_billable_leakage_effect",
    ]:
        bridge[f"{col}_pct"] = bridge[col] / bridge["total_variance"].replace({0: pd.NA})

    return bridge.reset_index()
