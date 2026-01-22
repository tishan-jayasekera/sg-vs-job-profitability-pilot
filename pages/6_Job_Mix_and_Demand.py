from __future__ import annotations

import streamlit as st

from src.config import load_config
from src.data.loader import load_processed_table
from src.metrics.capacity import capacity_pack
from src.metrics.job_mix import job_mix_pack
from src.ui.layout import render_header, render_filter_chips
from src.ui.charts import line_chart, scatter_chart
from src.ui.formatting import fmt_currency


config = load_config()
filters = st.session_state.get("global_filters", {})

render_header("Job Mix & Demand", ["Company", "Job Mix"])
render_filter_chips({k: v for k, v in filters.items() if isinstance(v, list) and v})

try:
    fact_job_task = load_processed_table(config.data_dir, "fact_job_task_month")
    fact_timesheet = load_processed_table(config.data_dir, "fact_timesheet_day_enriched")
except FileNotFoundError as exc:
    st.error(str(exc))
    st.stop()

cohort = st.selectbox("Cohort Definition", ["A", "B", "C"], index=0)
st.session_state["cohort_definition"] = cohort

weeks_in_window = 4
capacity = capacity_pack(fact_timesheet, ["staff_name"], weeks_in_window)
job_mix = job_mix_pack(fact_job_task, capacity, weeks_in_window, util_target=0.75)

st.subheader("Job Mix KPIs")
summary = job_mix.agg(
    job_count=("job_count", "sum"),
    total_quoted_value=("total_quoted_amount", "sum"),
    total_quoted_hours=("total_quoted_hours", "sum"),
)
cols = st.columns(4)
cols[0].metric("Job count", f"{summary['job_count']:,.0f}")
cols[1].metric("Total quoted value", fmt_currency(summary["total_quoted_value"]))
cols[2].metric("Total quoted hours", f"{summary['total_quoted_hours']:,.0f}")
cols[3].metric("Implied FTE", f"{job_mix['implied_fte_required'].mean():.2f}")

st.subheader("Trend")
if "month_key" in job_mix.columns:
    trend = job_mix.groupby("month_key", dropna=False)["job_count"].sum().reset_index()
    chart = line_chart(trend, "month_key", "job_count")
    st.altair_chart(chart, use_container_width=True)

st.subheader("Job Quadrant")
quad = job_mix[["avg_quoted_hours_per_job", "avg_quoted_amount_per_job"]].dropna()
quad_chart = scatter_chart(quad, "avg_quoted_hours_per_job", "avg_quoted_amount_per_job")
st.altair_chart(quad_chart, use_container_width=True)
