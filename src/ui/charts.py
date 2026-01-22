from __future__ import annotations

import altair as alt
import pandas as pd


def bar_chart(df: pd.DataFrame, x: str, y: str, color: str | None = None, height: int = 260):
    chart = alt.Chart(df).mark_bar().encode(x=x, y=y)
    if color:
        chart = chart.encode(color=color)
    return chart.properties(height=height)


def scatter_chart(df: pd.DataFrame, x: str, y: str, color: str | None = None, size: str | None = None, height: int = 260):
    chart = alt.Chart(df).mark_circle(opacity=0.8).encode(x=x, y=y)
    if color:
        chart = chart.encode(color=color)
    if size:
        chart = chart.encode(size=size)
    return chart.properties(height=height)


def line_chart(df: pd.DataFrame, x: str, y: str, color: str | None = None, height: int = 260):
    chart = alt.Chart(df).mark_line().encode(x=x, y=y)
    if color:
        chart = chart.encode(color=color)
    return chart.properties(height=height)
