from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


REQUIRED_FACT_TIMESHEET_COLUMNS = {
    "department_final",
    "job_category",
    "task_name",
    "staff_name",
    "month_key",
    "hours_raw",
    "base_cost",
    "rev_alloc",
    "quoted_time_total",
    "quoted_amount_total",
    "quote_match_flag",
    "is_billable",
    "utilisation_target",
    "fte_hours_scaling",
    "breakdown",
}

SOFT_FACT_TIMESHEET_COLUMNS = {
    "job_status",
    "job_due_date",
    "job_completed_date",
    "client",
    "business_unit",
    "role",
    "function",
    "onshore_flag",
    "state",
    "job_no",
}

REQUIRED_FACT_JOB_TASK_MONTH_COLUMNS = {
    "job_no",
    "task_name",
    "month_key",
    "department_final",
    "job_category",
    "hours_raw_sum",
    "base_cost_sum",
    "rev_alloc_sum",
    "quoted_time_total",
    "quoted_amount_total",
}

SOFT_FACT_JOB_TASK_MONTH_COLUMNS = {
    "quote_match_flag",
}

REQUIRED_AUDIT_REVENUE_COLUMNS = {
    "job_no",
    "month_key",
    "rev_alloc_total",
    "revenue_pool_total",
    "diff",
}

REQUIRED_AUDIT_UNALLOCATED_COLUMNS = {
    "month_key",
    "unallocated_revenue",
}


@dataclass(frozen=True)
class SchemaResult:
    missing_required: set[str]
    missing_soft: set[str]

    @property
    def ok(self) -> bool:
        return not self.missing_required


def _check_columns(columns: Iterable[str], required: set[str], soft: set[str]) -> SchemaResult:
    col_set = set(columns)
    missing_required = required - col_set
    missing_soft = soft - col_set
    return SchemaResult(missing_required=missing_required, missing_soft=missing_soft)


def validate_fact_timesheet(df) -> SchemaResult:
    result = _check_columns(df.columns, REQUIRED_FACT_TIMESHEET_COLUMNS, SOFT_FACT_TIMESHEET_COLUMNS)
    if result.missing_required:
        raise ValueError(f"fact_timesheet_day_enriched missing columns: {sorted(result.missing_required)}")
    return result


def validate_fact_job_task_month(df) -> SchemaResult:
    result = _check_columns(df.columns, REQUIRED_FACT_JOB_TASK_MONTH_COLUMNS, SOFT_FACT_JOB_TASK_MONTH_COLUMNS)
    if result.missing_required:
        raise ValueError(f"fact_job_task_month missing columns: {sorted(result.missing_required)}")
    return result


def validate_audit_revenue(df) -> SchemaResult:
    result = _check_columns(df.columns, REQUIRED_AUDIT_REVENUE_COLUMNS, set())
    if result.missing_required:
        raise ValueError(f"audit_revenue_reconciliation_job_month missing columns: {sorted(result.missing_required)}")
    return result


def validate_audit_unallocated(df) -> SchemaResult:
    result = _check_columns(df.columns, REQUIRED_AUDIT_UNALLOCATED_COLUMNS, set())
    if result.missing_required:
        raise ValueError(f"audit_unallocated_revenue missing columns: {sorted(result.missing_required)}")
    return result
