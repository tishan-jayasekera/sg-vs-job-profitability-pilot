from __future__ import annotations

import streamlit as st

from src.config import load_config
from src.data.loader import load_mart_table, load_processed_table
from src.data.semantic import month_key_to_period, leave_exclusion_mask
from src.metrics.utilisation import utilisation_pack
from src.metrics.quote_delivery import quote_delivery_pack
from src.metrics.rate_capture import rate_capture_pack
from src.ui.components import kpi_strip
from src.ui.layout import render_header, render_filter_chips
from src.ui.tables import drill_table, ranked_table
from src.ui.formatting import fmt_currency, fmt_percent, fmt_rate, fmt_hours
from src.ui.state import init_state, update_drill


config = load_config()
init_state()
filters = st.session_state.get("global_filters", {})


def apply_time_filter(df):
    if "month_key" not in df.columns:
        return df
    periods = month_key_to_period(df["month_key"])
    window = filters.get("window_value")
    if isinstance(window, int):
        latest = periods.max()
        if latest is pd.NaT:
            return df
        cutoff = latest - window + 1
        return df.loc[periods >= cutoff]
    if window == "FYTD":
        latest = periods.max()
        if latest is pd.NaT:
            return df
        fy_start = pd.Period(f"{latest.year}-07", freq="M") if latest.month >= 7 else pd.Period(f"{latest.year-1}-07", freq="M")
        return df.loc[periods >= fy_start]
    if window == "Custom":
        start = filters.get("start_month")
        end = filters.get("end_month")
        if start and end:
            return df.loc[(periods >= pd.Period(start, freq="M")) & (periods <= pd.Period(end, freq="M"))]
    return df


import pandas as pd

try:
    fact_timesheet = load_processed_table(config.data_dir, "fact_timesheet_day_enriched")
except FileNotFoundError as exc:
    st.error(str(exc))
    st.stop()
fact_timesheet = apply_time_filter(fact_timesheet)

if filters.get("exclude_leave"):
    fact_timesheet = fact_timesheet.loc[~leave_exclusion_mask(fact_timesheet)]

for col, values in filters.items():
    if col in fact_timesheet.columns and isinstance(values, list) and values:
        fact_timesheet = fact_timesheet.loc[fact_timesheet[col].isin(values)]

render_header("Executive Summary", ["Company"])
render_filter_chips({k: v for k, v in filters.items() if isinstance(v, list) and v})

profit = fact_timesheet.agg(
    revenue=("rev_alloc", "sum"),
    cost=("base_cost", "sum"),
    hours=("hours_raw", "sum"),
)
margin = profit["revenue"] - profit["cost"]
margin_pct = margin / profit["revenue"] if profit["revenue"] else 0
util = utilisation_pack(fact_timesheet, ["company"], exclude_leave=False)
util_pct = util["utilisation"].iloc[0] if not util.empty else 0
realised_rate = profit["revenue"] / profit["hours"] if profit["hours"] else 0

kpi_strip([
    ("Revenue", fmt_currency(profit["revenue"])),
    ("Cost", fmt_currency(profit["cost"])),
    ("Margin", fmt_currency(margin)),
    ("Margin %", fmt_percent(margin_pct)),
    ("Hours", fmt_hours(profit["hours"])),
    ("Realised Rate", fmt_rate(realised_rate)),
    ("Utilisation", fmt_percent(util_pct)),
])

st.subheader("Quote to Delivery")
quote_delivery = quote_delivery_pack(fact_timesheet, ["department_final"])
st.dataframe(quote_delivery, use_container_width=True)

st.subheader("Quote Rate vs Realised")
rate_capture = rate_capture_pack(fact_timesheet, ["department_final"])
st.dataframe(rate_capture, use_container_width=True)

st.subheader("Drill")
departments = sorted(fact_timesheet["department_final"].dropna().unique())
selected_dept = st.selectbox("Department", ["All"] + departments)
if selected_dept != "All":
    update_drill(selected_dept, None)
    drill_level = "department"
else:
    update_drill(None, None)
    drill_level = "company"

if drill_level == "company":
    drill_df = fact_timesheet.groupby("department_final", dropna=False)["rev_alloc"].sum().reset_index()
    drill_table(drill_df, "dept_drill")
else:
    categories = sorted(fact_timesheet.loc[fact_timesheet["department_final"] == selected_dept, "job_category"].dropna().unique())
    selected_cat = st.selectbox("Job Category", ["All"] + categories)
    if selected_cat != "All":
        update_drill(selected_dept, selected_cat)
        task_tab, staff_tab = st.tabs(["Tasks", "Staff"])
        with task_tab:
            task_df = fact_timesheet.loc[
                (fact_timesheet["department_final"] == selected_dept)
                & (fact_timesheet["job_category"] == selected_cat)
            ].groupby("task_name", dropna=False)["rev_alloc"].sum().reset_index()
            drill_table(task_df, "task_drill")
        with staff_tab:
            staff_df = fact_timesheet.loc[
                (fact_timesheet["department_final"] == selected_dept)
                & (fact_timesheet["job_category"] == selected_cat)
            ].groupby("staff_name", dropna=False)["rev_alloc"].sum().reset_index()
            drill_table(staff_df, "staff_drill")
    else:
        cat_df = fact_timesheet.loc[fact_timesheet["department_final"] == selected_dept].groupby("job_category", dropna=False)["rev_alloc"].sum().reset_index()
        drill_table(cat_df, "cat_drill")

st.subheader("Action Shortlist")
hotspots = quote_delivery.sort_values("hours_variance", ascending=False).head(10)
ranked_table(hotspots, "hotspots", "hours_variance")
