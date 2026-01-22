from __future__ import annotations

import sys

from src.config import load_config
from src.data.loader import load_processed_table
from src.data.schema import (
    validate_audit_revenue,
    validate_audit_unallocated,
    validate_fact_job_task_month,
    validate_fact_timesheet,
)


def main() -> int:
    config = load_config()
    try:
        fact_timesheet = load_processed_table(config.data_dir, "fact_timesheet_day_enriched")
        fact_job_task = load_processed_table(config.data_dir, "fact_job_task_month")
        audit_revenue = load_processed_table(config.data_dir, "audit_revenue_reconciliation_job_month")
        audit_unallocated = load_processed_table(config.data_dir, "audit_unallocated_revenue")
    except FileNotFoundError as exc:
        print(str(exc))
        return 1

    validate_fact_timesheet(fact_timesheet)
    validate_fact_job_task_month(fact_job_task)
    validate_audit_revenue(audit_revenue)
    validate_audit_unallocated(audit_unallocated)

    print("Inputs validated successfully")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
