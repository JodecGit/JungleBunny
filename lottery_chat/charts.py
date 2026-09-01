from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from lottery_chat.analyzer import (
    bonus_frequencies,
    filter_by_weekday,
    hot_cold,
    main_frequencies,
    weekday_number_matrix,
)
from lottery_chat.config import DISPLAY_NAME, NUMBER_MAX
from lottery_chat.models import Draw


def main_frequency_figure(draws: list[Draw], weekday: str | None = None) -> go.Figure:
    subset = filter_by_weekday(draws, weekday)
    freqs = main_frequencies(subset)
    label = weekday.title() if weekday else "all draws"
    df = pd.DataFrame({"number": list(freqs), "count": list(freqs.values())})
    fig = px.bar(
        df,
        x="number",
        y="count",
        title=f"{DISPLAY_NAME} main-number frequency ({label}, {len(subset)} draws)",
    )
    fig.update_layout(xaxis=dict(dtick=1), bargap=0.15)
    return fig


def bonus_frequency_figure(draws: list[Draw]) -> go.Figure:
    freqs = bonus_frequencies(draws)
    df = pd.DataFrame({"number": list(freqs), "count": list(freqs.values())})
    fig = px.bar(
        df,
        x="number",
        y="count",
        title=f"{DISPLAY_NAME} bonus-number frequency ({len(draws)} draws)",
        color_discrete_sequence=["#c9a227"],
    )
    fig.update_layout(xaxis=dict(dtick=1), bargap=0.15)
    return fig


def hot_cold_figure(draws: list[Draw], n: int = 10) -> go.Figure:
    freqs = main_frequencies(draws)
    hot, cold = hot_cold(freqs, n=n)
    hot_df = pd.DataFrame(hot, columns=["number", "count"]).assign(group="Hot")
    cold_df = pd.DataFrame(cold, columns=["number", "count"]).assign(group="Cold")
    df = pd.concat([hot_df, cold_df], ignore_index=True)
    fig = px.bar(
        df,
        x="number",
        y="count",
        color="group",
        barmode="group",
        title=f"{DISPLAY_NAME} hot vs cold mains (top/bottom {n})",
    )
    fig.update_layout(xaxis=dict(type="category"))
    return fig


def heatmap_figure(draws: list[Draw]) -> go.Figure:
    matrix = weekday_number_matrix(draws)
    z = [matrix["Wednesday"], matrix["Saturday"]]
    fig = go.Figure(
        data=go.Heatmap(
            z=z,
            x=list(range(1, NUMBER_MAX + 1)),
            y=["Wednesday", "Saturday"],
            colorscale="Blues",
            hovertemplate="Number %{x}<br>%{y}: %{z}<extra></extra>",
        )
    )
    fig.update_layout(
        title=f"{DISPLAY_NAME} main numbers by weekday",
        xaxis_title="Number",
        yaxis_title="Draw day",
    )
    return fig
