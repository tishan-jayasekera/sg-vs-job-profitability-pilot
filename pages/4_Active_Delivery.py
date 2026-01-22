from __future__ import annotations

import streamlit as st

from src.config import load_config
from src.data.loader import load_processed_table
from src.metrics.active_projects import active_projects_pack
from src.ui.layout import render_header, render_filter_chips
from src.exports import export_csv


config = load_config()
filters = st.session_state.get("global_filters", {})

render_header("Active Delivery", ["Company", "Active Delivery"])
render_filter_chips({k: v for k, v in filters.items() if isinstance(v, list) and v})

fact_timesheet = load_processed_table(config.data_dir, "fact_timesheet_day_enriched")
active_jobs = active_projects_pack(fact_timesheet, config.active_job_recency_days)

st.subheader("At-Risk Jobs")
active_jobs["risk_status"] = "on track"
active_jobs.loc[active_jobs["quote_consumed_pct"] > 0.9, "risk_status"] = "watch"
active_jobs.loc[active_jobs["quote_consumed_pct"] > 1.0, "risk_status"] = "at risk"

st.dataframe(active_jobs, use_container_width=True)
export_csv(active_jobs, "active_jobs.csv", "Export at-risk jobs")
