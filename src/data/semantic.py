from __future__ import annotations

import pandas as pd


CANONICAL_HIERARCHY = ["company", "department_final", "job_category", "task_name", "staff_name"]


def ensure_company(df: pd.DataFrame, company_label: str = "SG") -> pd.DataFrame:
    if "company" not in df.columns:
        df = df.copy()
        df["company"] = company_label
    return df


def month_key_to_period(series: pd.Series) -> pd.Series:
    def _parse(value) -> pd.Period:
        if pd.isna(value):
            return pd.NaT
        if isinstance(value, pd.Period):
            return value
        text = str(value)
        if len(text) == 6 and text.isdigit():
            return pd.Period(f"{text[:4]}-{text[4:]}", freq="M")
        if len(text) >= 7:
            return pd.Period(text[:7], freq="M")
        raise ValueError(f"Unsupported month_key format: {value}")

    return series.apply(_parse)


def add_aus_fy(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    periods = month_key_to_period(df["month_key"])
    years = periods.dt.year
    months = periods.dt.month
    fy_year = years.where(months <= 6, years + 1)
    df["aus_fy"] = "FY" + fy_year.astype("Int64").astype(str)
    return df


def leave_exclusion_mask(df: pd.DataFrame) -> pd.Series:
    return df["task_name"].astype(str).str.contains("leave", case=False, na=False)


def safe_quote_job_task(df: pd.DataFrame, include_cols: list[str] | None = None) -> pd.DataFrame:
    if "job_no" not in df.columns:
        raise ValueError("safe_quote_job_task requires job_no column")
    cols = [
        "job_no",
        "task_name",
        "quoted_time_total",
        "quoted_amount_total",
    ]
    if "quote_match_flag" in df.columns:
        cols.append("quote_match_flag")
    if include_cols:
        cols = list(dict.fromkeys(cols + include_cols))
    return df[cols].drop_duplicates(subset=["job_no", "task_name"]).copy()


def safe_quote_rollup(df: pd.DataFrame, group_keys: list[str]) -> pd.DataFrame:
    quote_df = safe_quote_job_task(df, include_cols=group_keys)
    rollup = (
        quote_df.groupby(group_keys, dropna=False)[
            ["quoted_time_total", "quoted_amount_total"]
        ]
        .sum()
        .rename(columns={
            "quoted_time_total": "quoted_hours",
            "quoted_amount_total": "quoted_amount",
        })
        .reset_index()
    )
    return rollup


def profitability_rollup(df: pd.DataFrame, group_keys: list[str]) -> pd.DataFrame:
    grouped = df.groupby(group_keys, dropna=False).agg(
        hours=("hours_raw", "sum"),
        cost=("base_cost", "sum"),
        revenue=("rev_alloc", "sum"),
    )
    grouped["margin"] = grouped["revenue"] - grouped["cost"]
    grouped["margin_pct"] = grouped["margin"] / grouped["revenue"].replace({0: pd.NA})
    grouped["realised_rate"] = grouped["revenue"] / grouped["hours"].replace({0: pd.NA})
    return grouped.reset_index()


def rate_rollups(df: pd.DataFrame, group_keys: list[str]) -> pd.DataFrame:
    realised = (
        df.groupby(group_keys, dropna=False)[["rev_alloc", "hours_raw"]]
        .sum()
        .reset_index()
    )
    realised["realised_rate"] = realised["rev_alloc"] / realised["hours_raw"].replace({0: pd.NA})

    quote = safe_quote_rollup(df, group_keys)
    quote["quote_rate"] = quote["quoted_amount"] / quote["quoted_hours"].replace({0: pd.NA})

    merged = realised.merge(quote, on=group_keys, how="left")
    return merged


def scope_creep(df: pd.DataFrame) -> pd.Series:
    if "quote_match_flag" not in df.columns:
        return pd.Series(0, index=df.index)
    flags = df["quote_match_flag"].astype(str).str.lower()
    return flags.isin({"no_match", "no match", "false", "0"})
