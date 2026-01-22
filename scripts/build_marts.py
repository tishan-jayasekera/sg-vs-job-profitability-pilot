from __future__ import annotations

import sys

from src.config import load_config
from src.data.loader import load_processed_table
from src.data.marts import build_all_marts


def main() -> int:
    config = load_config()
    try:
        fact_timesheet = load_processed_table(config.data_dir, "fact_timesheet_day_enriched")
        fact_job_task = load_processed_table(config.data_dir, "fact_job_task_month")
    except FileNotFoundError as exc:
        print(str(exc))
        return 1

    build_all_marts(
        fact_timesheet=fact_timesheet,
        fact_job_task_month=fact_job_task,
        data_dir=config.data_dir,
        recency_days=config.active_job_recency_days,
        weeks_in_window=4,
        util_target=0.75,
    )
    print("Marts built successfully")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
