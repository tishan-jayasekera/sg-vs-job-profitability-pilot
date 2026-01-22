from __future__ import annotations

import streamlit as st

from src.config import load_config
from src.data.loader import load_processed_table
from src.ui.state import init_state


st.set_page_config(page_title="SG Job Profitability OS", layout="wide")

config = load_config()
init_state()

try:
    fact_timesheet = load_processed_table(config.data_dir, "fact_timesheet_day_enriched")
except FileNotFoundError:
    fact_timesheet = None

st.sidebar.title("SG Profitability OS")

window_options = {
    "Last 3 months": 3,
    "Last 6 months": 6,
    "Last 12 months": 12,
    "Last 24 months": 24,
    "FYTD": "FYTD",
    "Custom": "Custom",
}

selected_window = st.sidebar.selectbox("Time window", list(window_options.keys()))
start_month = None
end_month = None
if selected_window == "Custom":
    start_month = st.sidebar.text_input("Start month (YYYY-MM)")
    end_month = st.sidebar.text_input("End month (YYYY-MM)")

active_only = st.sidebar.toggle("Active jobs only", value=False)
exclude_leave = st.sidebar.toggle("Exclude leave", value=True)
include_non_billable = st.sidebar.toggle("Include non-billable", value=True)

optional_filters = {}
if fact_timesheet is not None:
    for col in ["client", "business_unit", "role", "function", "onshore_flag", "job_status", "state"]:
        if col in fact_timesheet.columns:
            values = sorted([v for v in fact_timesheet[col].dropna().unique()])
            choice = st.sidebar.multiselect(col.replace("_", " ").title(), values)
            optional_filters[col] = choice

st.session_state["global_filters"] = {
    "time_window": selected_window,
    "window_value": window_options[selected_window],
    "start_month": start_month,
    "end_month": end_month,
    "active_only": active_only,
    "exclude_leave": exclude_leave,
    "include_non_billable": include_non_billable,
    **optional_filters,
}

st.sidebar.caption("Filters apply across pages")

st.title("SG Job Profitability OS")
st.write("Use the navigation sidebar to explore performance, quoting, capacity, and delivery.")
