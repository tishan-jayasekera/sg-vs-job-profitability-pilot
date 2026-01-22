from __future__ import annotations

import pandas as pd
import streamlit as st

from src.config import load_config
from src.data.cohorts import recency_weights
from src.data.loader import load_processed_table
from src.metrics.capacity import capacity_pack
from src.ui.layout import render_header, render_filter_chips
from src.ui.state import init_state
from src.ui.charts import scatter_chart
from src.exports import export_csv


config = load_config()
init_state()
filters = st.session_state.get("global_filters", {})

render_header("Capacity & Staffing", ["Company", "Capacity"])
render_filter_chips({k: v for k, v in filters.items() if isinstance(v, list) and v})

try:
    fact_timesheet = load_processed_table(config.data_dir, "fact_timesheet_day_enriched")
except FileNotFoundError as exc:
    st.error(str(exc))
    st.stop()

weeks_in_window = 4
capacity = capacity_pack(fact_timesheet, ["staff_name"], weeks_in_window)

st.subheader("Capacity Overview")
capacity_summary = capacity.agg(
    total_supply=("period_capacity", "sum"),
    billable_capacity=("billable_capacity", "sum"),
    trailing_load=("trailing_billable_load", "sum"),
    headroom=("headroom", "sum"),
)

cols = st.columns(4)
cols[0].metric("Total supply", f"{capacity_summary['total_supply']:,.0f}h")
cols[1].metric("Billable capacity", f"{capacity_summary['billable_capacity']:,.0f}h")
cols[2].metric("Trailing load", f"{capacity_summary['trailing_load']:,.0f}h")
cols[3].metric("Headroom", f"{capacity_summary['headroom']:,.0f}h")

quote_plan = st.session_state.get("quote_plan")
if quote_plan:
    st.subheader("Staffing Recommender")
    plan_df = pd.DataFrame(quote_plan)
    task_hours = plan_df[["task_name", "suggested_hours"]].groupby("task_name").sum().reset_index()

    weights = recency_weights(fact_timesheet["month_key"], config.recency_half_life_months)
    fact_timesheet = fact_timesheet.assign(recency_weight=weights)
    staff_skill = fact_timesheet.groupby(["staff_name", "task_name"]).agg(
        weighted_hours=("recency_weight", lambda s: s.sum()),
        hours=("hours_raw", "sum"),
    ).reset_index()

    recommendations = []
    for _, row in task_hours.iterrows():
        candidates = staff_skill.loc[staff_skill["task_name"] == row["task_name"]].copy()
        candidates = candidates.sort_values("weighted_hours", ascending=False).head(3)
        for _, cand in candidates.iterrows():
            recommendations.append({
                "task_name": row["task_name"],
                "planned_hours": row["suggested_hours"],
                "staff_name": cand["staff_name"],
                "capability_score": cand["weighted_hours"],
            })

    rec_df = pd.DataFrame(recommendations)
    st.dataframe(rec_df, use_container_width=True)
    export_csv(rec_df, "staffing_plan.csv", "Export staffing plan")

st.subheader("Staff Scatter")
scatter = capacity[["staff_name", "headroom", "trailing_billable_load"]].copy()
scatter["utilisation_gap"] = capacity["utilisation_target"] - (capacity["trailing_billable_load"] / capacity["period_capacity"].replace({0: pd.NA}))
chart = scatter_chart(scatter, "headroom", "utilisation_gap", size="trailing_billable_load")
st.altair_chart(chart, use_container_width=True)
