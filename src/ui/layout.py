from __future__ import annotations

import streamlit as st


def render_header(time_window_label: str, breadcrumb: list[str]) -> None:
    with st.container():
        st.markdown("## SG Job Profitability OS")
        st.caption(time_window_label)
        if breadcrumb:
            st.markdown(" ▸ ".join(breadcrumb))


def render_filter_chips(filters: dict[str, str]) -> None:
    if not filters:
        return
    chips = [f"{key}: {value}" for key, value in filters.items() if value]
    st.markdown(" ".join([f"`{chip}`" for chip in chips]))
