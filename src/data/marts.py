from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.data.semantic import (
    add_aus_fy,
    ensure_company,
    leave_exclusion_mask,
    profitability_rollup,
    rate_rollups,
    safe_quote_rollup,
)
from src.metrics.quote_delivery import quote_delivery_pack
from src.metrics.utilisation import utilisation_pack
from src.metrics.capacity import capacity_pack
from src.metrics.job_mix import job_mix_pack
from src.metrics.active_projects import active_projects_pack


def _write_mart(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix == ".parquet":
        df.to_parquet(path, index=False)
    else:
        df.to_csv(path, index=False)


def build_cube_dept_month(df: pd.DataFrame) -> pd.DataFrame:
    df = ensure_company(add_aus_fy(df))
    group_keys = ["company", "department_final", "month_key"]
    profit = profitability_rollup(df, group_keys)
    rates = rate_rollups(df, group_keys)
    quote = safe_quote_rollup(df, group_keys)
    merged = profit.merge(rates, on=group_keys, how="left").merge(quote, on=group_keys, how="left")
    return merged


def build_cube_dept_category_month(df: pd.DataFrame) -> pd.DataFrame:
    df = ensure_company(add_aus_fy(df))
    group_keys = ["company", "department_final", "job_category", "month_key"]
    profit = profitability_rollup(df, group_keys)
    rates = rate_rollups(df, group_keys)
    quote = safe_quote_rollup(df, group_keys)
    return profit.merge(rates, on=group_keys, how="left").merge(quote, on=group_keys, how="left")


def build_cube_dept_category_task(df: pd.DataFrame) -> pd.DataFrame:
    df = ensure_company(add_aus_fy(df))
    group_keys = ["company", "department_final", "job_category", "task_name"]
    profit = profitability_rollup(df, group_keys)
    quote = safe_quote_rollup(df, group_keys)
    delivery = quote_delivery_pack(df, group_keys)
    return profit.merge(quote, on=group_keys, how="left").merge(delivery, on=group_keys, how="left")


def build_cube_dept_category_staff(df: pd.DataFrame) -> pd.DataFrame:
    df = ensure_company(add_aus_fy(df))
    group_keys = ["company", "department_final", "job_category", "staff_name"]
    profit = profitability_rollup(df, group_keys)
    quote = safe_quote_rollup(df, group_keys)
    util = utilisation_pack(df, group_keys, exclude_leave=True)
    return profit.merge(quote, on=group_keys, how="left").merge(util, on=group_keys, how="left")


def build_active_jobs_snapshot(df: pd.DataFrame, recency_days: int) -> pd.DataFrame:
    df = ensure_company(add_aus_fy(df))
    return active_projects_pack(df, recency_days)


def build_job_mix_month(df: pd.DataFrame, capacity_df: pd.DataFrame, weeks_in_window: int, util_target: float) -> pd.DataFrame:
    df = ensure_company(add_aus_fy(df))
    return job_mix_pack(df, capacity_df, weeks_in_window, util_target)


def build_all_marts(
    fact_timesheet: pd.DataFrame,
    fact_job_task_month: pd.DataFrame,
    data_dir: Path,
    recency_days: int,
    weeks_in_window: int,
    util_target: float,
) -> dict[str, pd.DataFrame]:
    marts = {
        "cube_dept_month": build_cube_dept_month(fact_timesheet),
        "cube_dept_category_month": build_cube_dept_category_month(fact_timesheet),
        "cube_dept_category_task": build_cube_dept_category_task(fact_timesheet),
        "cube_dept_category_staff": build_cube_dept_category_staff(fact_timesheet),
    }

    marts["active_jobs_snapshot"] = build_active_jobs_snapshot(fact_timesheet, recency_days)

    capacity = capacity_pack(fact_timesheet, ["staff_name"], weeks_in_window)
    marts["job_mix_month"] = build_job_mix_month(fact_job_task_month, capacity, weeks_in_window, util_target)

    for name, df in marts.items():
        _write_mart(df, data_dir / "marts" / f"{name}.parquet")

    return marts
