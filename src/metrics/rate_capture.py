from __future__ import annotations

import pandas as pd

from src.data.semantic import rate_rollups


def rate_capture_pack(df: pd.DataFrame, group_keys: list[str]) -> pd.DataFrame:
    rates = rate_rollups(df, group_keys)
    rates["rate_variance"] = rates["realised_rate"] - rates["quote_rate"]

    weighted = rates.copy()
    weighted["quote_rate_wtd"] = weighted["quoted_amount"] / weighted["quoted_hours"].replace({0: pd.NA})
    weighted["realised_rate_wtd"] = weighted["rev_alloc"] / weighted["hours_raw"].replace({0: pd.NA})
    return rates.merge(
        weighted[group_keys + ["quote_rate_wtd", "realised_rate_wtd"]], on=group_keys, how="left"
    )
