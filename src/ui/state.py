from __future__ import annotations

import streamlit as st


DEFAULT_STATE = {
    "selected_department_final": None,
    "selected_job_category": None,
    "drill_level": "company",
    "category_subtab": "tasks",
    "global_filters": {},
    "quote_plan": None,
    "cohort_definition": "A",
}


def init_state() -> None:
    for key, value in DEFAULT_STATE.items():
        if key not in st.session_state:
            st.session_state[key] = value


def update_drill(dept: str | None, category: str | None) -> None:
    st.session_state["selected_department_final"] = dept
    st.session_state["selected_job_category"] = category
    if dept and category:
        st.session_state["drill_level"] = "category"
    elif dept:
        st.session_state["drill_level"] = "department"
    else:
        st.session_state["drill_level"] = "company"
