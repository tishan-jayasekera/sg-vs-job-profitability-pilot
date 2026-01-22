from __future__ import annotations

import streamlit as st

from src.config import load_config
from src.data.loader import load_processed_table
from src.ui.layout import render_header


config = load_config()
render_header("Data Quality & QA", ["Company", "QA"])

try:
    audit_revenue = load_processed_table(config.data_dir, "audit_revenue_reconciliation_job_month")
    audit_unallocated = load_processed_table(config.data_dir, "audit_unallocated_revenue")
except FileNotFoundError as exc:
    st.error(str(exc))
    st.stop()

st.subheader("Revenue Reconciliation")
st.dataframe(audit_revenue, use_container_width=True)

st.subheader("Unallocated Revenue")
st.dataframe(audit_unallocated, use_container_width=True)

st.subheader("Quote Match Coverage")
try:
    fact_timesheet = load_processed_table(config.data_dir, "fact_timesheet_day_enriched")
except FileNotFoundError as exc:
    st.error(str(exc))
    st.stop()
if "quote_match_flag" in fact_timesheet.columns:
    coverage = fact_timesheet["quote_match_flag"].value_counts(dropna=False).reset_index()
    st.dataframe(coverage, use_container_width=True)

st.subheader("Anomalies")
missing_quote = fact_timesheet.loc[fact_timesheet["quoted_time_total"].isna()].head(50)
st.dataframe(missing_quote, use_container_width=True)
