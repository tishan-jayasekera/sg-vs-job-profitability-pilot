from __future__ import annotations

import streamlit as st

from src.ui.layout import render_header


render_header("Glossary & Method", ["Company", "Glossary"])

st.subheader("Key Definitions")

st.markdown(
    """
- **rev_alloc**: Revenue allocated at the atomic fact level. All revenue rollups use Σ `rev_alloc`.
- **realised_rate**: Σ `rev_alloc` / Σ `hours_raw`.
- **quote_rate**: Σ `quoted_amount` / Σ `quoted_hours` after deduping at `(job_no, task_name)`.
- **hours_variance**: Actual hours minus quoted hours.
- **scope_creep**: Hours where `quote_match_flag` indicates no match.
- **capacity model**: Weekly capacity = `38 × fte_hours_scaling`. Period capacity = weekly capacity × weeks in window.
- **leave exclusion**: Rows with task_name containing "leave" (case-insensitive) are excluded from utilisation by default.
- **safe quote rollups**: Quote fields repeat on daily rows; rollups dedupe at `(job_no, task_name)` before summing.
"""
)
