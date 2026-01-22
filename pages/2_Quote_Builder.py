from __future__ import annotations

import pandas as pd
import streamlit as st

from src.config import load_config
from src.data.cohorts import cohort_stats, recency_weights
from src.data.loader import load_mart_table, load_processed_table
from src.data.semantic import month_key_to_period
from src.ui.formatting import fmt_currency, fmt_percent
from src.ui.layout import render_header, render_filter_chips
from src.ui.state import init_state
from src.exports import export_csv, export_json


config = load_config()
init_state()
filters = st.session_state.get("global_filters", {})

render_header("Quote Builder", ["Company", "Quote Builder"])
render_filter_chips({k: v for k, v in filters.items() if isinstance(v, list) and v})

try:
    fact_timesheet = load_processed_table(config.data_dir, "fact_timesheet_day_enriched")
except FileNotFoundError as exc:
    st.error(str(exc))
    st.stop()

try:
    mart_tasks = load_mart_table(config.data_dir, "cube_dept_category_task", fallback_processed="fact_timesheet_day_enriched")
except FileNotFoundError as exc:
    st.error(str(exc))
    st.stop()


dept_options = sorted(fact_timesheet["department_final"].dropna().unique())
dept = st.selectbox("Department", dept_options)
cat_options = sorted(fact_timesheet.loc[fact_timesheet["department_final"] == dept, "job_category"].dropna().unique())
category = st.selectbox("Job Category", cat_options)

benchmark_window = st.selectbox("Benchmark Window", [3, 6, 12, 24])
recency_on = st.toggle("Recency-weighted", value=True)
active_only = st.toggle("Active staff only", value=True)

subset = fact_timesheet.loc[(fact_timesheet["department_final"] == dept) & (fact_timesheet["job_category"] == category)]
periods = month_key_to_period(subset["month_key"])
latest = periods.max()
if latest is not pd.NaT:
    cutoff = latest - benchmark_window + 1
    subset = subset.loc[periods >= cutoff]

if active_only:
    active_staff = subset.groupby("staff_name")["hours_raw"].sum()
    subset = subset.loc[subset["staff_name"].isin(active_staff[active_staff > 0].index)]

weights = recency_weights(subset["month_key"], config.recency_half_life_months) if recency_on else pd.Series(1, index=subset.index)

mart_subset = mart_tasks.loc[
    (mart_tasks["department_final"] == dept) & (mart_tasks["job_category"] == category)
]

task_template = mart_subset[["task_name", "quoted_hours", "quoted_amount", "hours", "overrun_rate"]].copy()
if task_template.empty:
    task_template = subset.groupby("task_name", dropna=False).agg(
        quoted_hours=("quoted_time_total", "median"),
        quoted_amount=("quoted_amount_total", "median"),
        hours=("hours_raw", "median"),
    ).reset_index()
    task_template["overrun_rate"] = pd.NA

if "quoted_hours" not in task_template.columns:
    task_template = task_template.rename(columns={"quoted_time_total": "quoted_hours", "quoted_amount_total": "quoted_amount"})

task_template["suggested_hours"] = task_template["quoted_hours"].fillna(task_template["hours"])

task_template["optional"] = False

st.subheader("Task Template")
edited = st.data_editor(task_template, num_rows="dynamic", use_container_width=True)

planned_hours = edited["suggested_hours"].sum()
if edited["quoted_amount"].notna().any():
    quote_amount = edited["quoted_amount"].sum()
else:
    quote_amount = planned_hours * (subset["rev_alloc"].sum() / subset["hours_raw"].sum())

cost_rate = (subset["base_cost"].sum() / subset["hours_raw"].sum()) if subset["hours_raw"].sum() else 0
implied_cost = planned_hours * cost_rate
margin = quote_amount - implied_cost
margin_pct = margin / quote_amount if quote_amount else 0

stats = cohort_stats(subset, recency_on, config.active_staff_recency_months)

st.subheader("Economics")
cols = st.columns(5)
cols[0].metric("Planned hours", f"{planned_hours:,.1f}")
cols[1].metric("Recommended quote", fmt_currency(quote_amount))
cols[2].metric("Implied cost", fmt_currency(implied_cost))
cols[3].metric("Expected margin", fmt_currency(margin))
cols[4].metric("Margin %", fmt_percent(margin_pct))

st.caption(f"n_jobs: {stats.n_jobs} | n_active_staff: {stats.n_active_staff} | {stats.date_span} | recency weighted: {stats.recency_weighted}")

if st.button("Save quote plan"):
    st.session_state["quote_plan"] = edited.to_dict(orient="records")

export_csv(edited, "quote_plan.csv", "Export quote plan CSV")
export_json(edited.to_dict(orient="records"), "quote_plan.json", "Export quote plan JSON")

if st.button("Send to Capacity Planner"):
    st.switch_page("pages/3_Capacity_Staffing.py")
