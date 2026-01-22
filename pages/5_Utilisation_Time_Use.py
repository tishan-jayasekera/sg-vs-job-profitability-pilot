from __future__ import annotations

import streamlit as st

from src.config import load_config
from src.data.loader import load_processed_table
from src.metrics.utilisation import utilisation_pack, leakage_breakdown
from src.ui.layout import render_header, render_filter_chips
from src.ui.charts import scatter_chart, bar_chart


config = load_config()
filters = st.session_state.get("global_filters", {})

render_header("Utilisation & Time Use", ["Company", "Utilisation"])
render_filter_chips({k: v for k, v in filters.items() if isinstance(v, list) and v})

try:
    fact_timesheet = load_processed_table(config.data_dir, "fact_timesheet_day_enriched")
except FileNotFoundError as exc:
    st.error(str(exc))
    st.stop()
util = utilisation_pack(fact_timesheet, ["staff_name", "department_final"], exclude_leave=True)

st.subheader("Staff Scatter")
scatter = util.copy()
scatter["non_billable_share"] = 1 - scatter["utilisation"].fillna(0)
chart = scatter_chart(scatter, "utilisation", "non_billable_share", color="department_final")
st.altair_chart(chart, use_container_width=True)

st.subheader("Department Summary")
breakdown = leakage_breakdown(fact_timesheet, ["department_final"], breakdown_field="breakdown")
bar = bar_chart(breakdown, "department_final", "hours_raw", color="breakdown")
st.altair_chart(bar, use_container_width=True)
