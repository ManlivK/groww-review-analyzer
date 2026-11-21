"""Plotly chart builders with a shared premium light analytics theme."""

from __future__ import annotations

from typing import Any, Sequence

import plotly.graph_objects as go

PALETTE = {
    "teal": "#268C78",
    "blue": "#6E8CA0",
    "amber": "#C98B4B",
    "red": "#C96F5A",
    "purple": "#8D7B98",
}

_TEXT = "#343A35"
_MUTED = "#73766F"
_GRID = "#D8D0C2"
_SURFACE = "#FFFDF8"

_LEGACY_COLORS = {
    "#26B99A": PALETTE["teal"],
    "#4C8DFF": PALETTE["blue"],
    "#F4B860": PALETTE["amber"],
    "#EF6F6C": PALETTE["red"],
    "#9B8CFF": PALETTE["purple"],
}


def apply_layout(fig: go.Figure, *, height: int = 330, showlegend: bool = False) -> go.Figure:
    """Apply the shared light theme to a Plotly figure."""
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"family": "Arial, sans-serif", "color": _MUTED, "size": 12},
        title={"font": {"color": _TEXT, "size": 14}, "x": 0.02, "xanchor": "left"},
        margin={"l": 55, "r": 24, "t": 44, "b": 45},
        showlegend=showlegend,
        legend={
            "orientation": "h",
            "y": 1.16,
            "x": 0,
            "font": {"color": _MUTED, "size": 11},
        },
        hoverlabel={
            "bgcolor": _SURFACE,
            "bordercolor": _GRID,
            "font": {"color": _TEXT, "size": 12},
        },
    )
    fig.update_xaxes(
        showgrid=False,
        zeroline=False,
        linecolor=_GRID,
        tickfont={"color": _MUTED},
        title_font={"color": _MUTED, "size": 11},
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor=_GRID,
        gridwidth=1,
        zeroline=False,
        linecolor=_GRID,
        tickfont={"color": _MUTED},
        title_font={"color": _MUTED, "size": 11},
    )
    return fig


def line_chart(
    labels: Sequence[str],
    values: Sequence[float],
    name: str,
    *,
    title: str = "",
    color: str = PALETTE["teal"],
    y_title: str = "",
    height: int = 330,
) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=list(labels),
            y=list(values),
            name=name,
            mode="lines+markers",
            line={"color": color, "width": 3, "shape": "spline", "smoothing": 0.5},
            marker={"color": color, "size": 7, "line": {"color": _SURFACE, "width": 2}},
            hovertemplate="%{x}<br>%{y:.2f}<extra></extra>",
            fill="tozeroy",
            fillcolor="rgba(38,140,120,0.10)" if color == PALETTE["teal"] else "rgba(110,140,160,0.10)",
        )
    )
    fig.update_layout(title_text=title)
    if y_title:
        fig.update_yaxes(title_text=y_title)
    return apply_layout(fig, height=height)


def rating_trend_chart(
    labels: Sequence[str],
    values: Sequence[float],
    *,
    title: str = "",
    y_title: str = "Rating (out of 5)",
) -> go.Figure:
    fig = line_chart(
        labels,
        values,
        "Average rating",
        title=title,
        y_title=y_title,
        height=285,
    )
    fig.update_layout(
        margin={"l": 52, "r": 18, "t": 40, "b": 42},
        modebar={
            "bgcolor": "rgba(255, 253, 248, 0.94)",
            "color": _MUTED,
            "activecolor": PALETTE["teal"],
            "orientation": "h",
        },
        hoverlabel={
            "bgcolor": _SURFACE,
            "bordercolor": _GRID,
            "font": {"color": _TEXT, "size": 12},
            "align": "left",
        },
    )
    fig.update_xaxes(
        tickangle=-35,
        tickfont={"color": _MUTED, "size": 11},
        automargin=True,
    )
    fig.update_yaxes(
        range=[0, 5],
        tickvals=[0, 1, 2, 3, 4, 5],
        gridcolor="#CFC6B6",
        gridwidth=1.3,
        tickfont={"color": _MUTED, "size": 11},
        automargin=True,
    )
    return fig


def bar_chart(
    labels: Sequence[str],
    values: Sequence[float],
    *,
    title: str = "",
    color: str = PALETTE["teal"],
    y_title: str = "",
    height: int = 330,
    text_template: str = "%{y:,}",
) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=list(labels),
            y=list(values),
            marker={"color": color, "line": {"color": _SURFACE, "width": 1}},
            texttemplate=text_template,
            textposition="outside",
            textfont={"color": _TEXT, "size": 10},
            hovertemplate="%{x}<br>%{y:,}<extra></extra>",
            width=0.6,
        )
    )
    fig.update_layout(title_text=title, bargap=0.28)
    fig.update_xaxes(type="category")
    if y_title:
        fig.update_yaxes(title_text=y_title)
    fig.update_yaxes(range=[0, max(values) * 1.18 if values else 1])
    return apply_layout(fig, height=height)


def donut_chart(
    labels: Sequence[str],
    values: Sequence[float],
    *,
    title: str = "",
    colors: Sequence[str] | None = None,
    height: int = 330,
) -> go.Figure:
    chart_colors = [_LEGACY_COLORS.get(color, color) for color in colors] if colors else None
    fig = go.Figure()
    fig.add_trace(
        go.Pie(
            labels=list(labels),
            values=list(values),
            hole=0.64,
            marker={"colors": chart_colors, "line": {"color": _SURFACE, "width": 2}},
            textinfo="label+percent",
            textfont={"color": _TEXT, "size": 11},
            hovertemplate="%{label}<br>%{value:,} (%{percent})<extra></extra>",
            sort=False,
        )
    )
    fig.update_layout(title_text=title)
    return apply_layout(fig, height=height, showlegend=False)


def stacked_bar_chart(
    labels: Sequence[str],
    series: dict[str, Sequence[float]],
    *,
    title: str = "",
    colors: Sequence[str] | None = None,
    y_title: str = "",
    height: int = 330,
) -> go.Figure:
    fig = go.Figure()
    palette = list(colors) if colors else list(PALETTE.values())
    for index, (name, values) in enumerate(series.items()):
        fig.add_trace(
            go.Bar(
                x=list(labels),
                y=list(values),
                name=name,
                marker_color=palette[index % len(palette)],
                hovertemplate="%{x}<br>" + name + ": %{y:,}<extra></extra>",
            )
        )
    fig.update_layout(title_text=title, barmode="stack", bargap=0.3)
    if y_title:
        fig.update_yaxes(title_text=y_title)
    fig = apply_layout(fig, height=height, showlegend=True)
    fig.update_layout(
        margin={"t": 96},
        title={"y": 0.97, "yanchor": "top", "yref": "container"},
        legend={"y": 1.03, "yanchor": "bottom", "x": 0, "xanchor": "left"},
    )
    return fig


def horizontal_bar_chart(
    labels: Sequence[str],
    values: Sequence[float],
    *,
    title: str = "",
    color: str = PALETTE["blue"],
    height: int = 330,
    text_template: str = "%{x:,}",
) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=list(values),
            y=list(labels),
            orientation="h",
            marker={"color": color, "line": {"color": _SURFACE, "width": 1}},
            texttemplate=text_template,
            textposition="outside",
            textfont={"color": _TEXT, "size": 10},
            hovertemplate="%{y}<br>%{x:,}<extra></extra>",
            width=0.55,
        )
    )
    fig.update_layout(title_text=title, bargap=0.3)
    fig.update_xaxes(range=[0, max(values) * 1.2 if values else 1])
    fig.update_yaxes(autorange="reversed")
    return apply_layout(fig, height=height)


def empty_figure(message: str = "No data available") -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        x=0.5,
        y=0.5,
        showarrow=False,
        font={"color": _MUTED, "size": 13},
    )
    return apply_layout(fig, height=260)
