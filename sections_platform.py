"""Consolidated Product Intelligence sections for the Groww Review Analyzer."""

from __future__ import annotations

from datetime import datetime
from html import escape
from typing import Any

import streamlit as st

from components.charts import (
    PALETTE,
    bar_chart,
    horizontal_bar_chart,
    line_chart,
    rating_trend_chart,
    stacked_bar_chart,
)
from components.ui import badge, caption, chart, kpi_row, panel, section_title
from data.validation import load_validation_records, summarise_areas, summarise_counts

CLEANED_REVIEW_COUNT = 6042
APPROVED_FEE_CLAIMS: list[str] = []

PIPELINE_STEPS = [
    {
        "number": "01",
        "title": "Play Store collection",
        "detail": "Public reviews are collected from the Groww Play Store listing.",
        "kind": "standard",
        "outputs": [],
    },
    {
        "number": "02",
        "title": "Data cleaning",
        "detail": "Collected reviews are cleaned and prepared for analysis.",
        "kind": "standard",
        "outputs": [],
    },
    {
        "number": "03",
        "title": "AI theme discovery and classification",
        "detail": "AI groups recurring topics into T1–T5 themes and assigns reviews to them.",
        "kind": "standard",
        "outputs": [],
    },
    {
        "number": "04",
        "title": "Product insights",
        "detail": "Themes, pain points and positive feedback are synthesised into opportunities.",
        "kind": "standard",
        "outputs": [],
    },
    {
        "number": "05",
        "title": "Fee fact-checking",
        "detail": "Fee claims are checked against official sources and marked approved or provisional.",
        "kind": "standard",
        "outputs": [],
    },
    {
        "number": "06",
        "title": "Human approval",
        "detail": "A person reviews fee claims and report content before publication.",
        "kind": "approval",
        "outputs": [],
    },
    {
        "number": "07",
        "title": "Weekly report outputs",
        "detail": "Approved findings become the weekly report with a four-week comparison.",
        "kind": "output",
        "outputs": ["Google Docs report", "Gmail draft / publication", "Streamlit dashboard"],
    },
]

_WORKFLOW_CONNECTOR_PATHS = {
    "right": (
        '<path class="ri-workflow-path-horizontal" d="M3 16 H25 M20 11 L25 16 L20 21"/>'
        '<path class="ri-workflow-path-vertical" d="M16 3 V25 M11 20 L16 25 L21 20"/>'
    ),
    "left": (
        '<path class="ri-workflow-path-horizontal" d="M29 16 H7 M12 11 L7 16 L12 21"/>'
        '<path class="ri-workflow-path-vertical" d="M16 3 V25 M11 20 L16 25 L21 20"/>'
    ),
    "down": '<path class="ri-workflow-path-vertical" d="M16 3 V25 M11 20 L16 25 L21 20"/>',
}


def _workflow_connector(direction: str, extra_class: str = "") -> str:
    classes = f"ri-workflow-connector ri-workflow-connector-{direction} {extra_class}".strip()
    return (
        f'<svg class="{classes}" viewBox="0 0 32 32" aria-hidden="true" focusable="false">'
        f"{_WORKFLOW_CONNECTOR_PATHS[direction]}</svg>"
    )


ROLE_CARDS = [
    ("n8n", "Orchestration", "Coordinates collection, cleaning, AI hand-offs and delivery."),
    ("AI processing", "Analysis", "Discovers themes, classifies reviews and drafts recommendations."),
    ("Streamlit", "Presentation", "Reads report.json and presents six views without changing data."),
]


def _get(data: dict[str, Any], section: str, key: str, default: Any = None) -> Any:
    return data.get(section, {}).get(key, default)


def _format_date(value: str) -> str:
    if not value:
        return "Not available"
    try:
        return datetime.strptime(value, "%Y-%m-%d").strftime("%d %b %Y")
    except (TypeError, ValueError):
        return str(value)


def _window(start: Any, end: Any) -> str:
    if not start or not end:
        return "Not available"
    return f"{_format_date(start)} – {_format_date(end)}"


def _kpi_value(data: dict[str, Any], label: str, default: str = "—") -> str:
    for row in _get(data, "overview", "kpis", []):
        if row.get("label") == label:
            return str(row.get("value", default))
    return default


def _rating_movement(previous: float, recent: float) -> str:
    delta = recent - previous
    if abs(delta) < 0.001:
        return "unchanged"
    direction = "up" if delta > 0 else "down"
    return f"{direction} {abs(delta):.2f} points"


def _tone(value: Any) -> str:
    return {
        "High": "high",
        "Medium": "medium",
        "Low": "low",
        "Positive": "positive",
        "Approved": "positive",
        "Not assessed": "neutral",
    }.get(str(value), "neutral")


def _render_reporting_period(data: dict[str, Any], *, scope: str = "") -> None:
    trend = _get(data, "overview", "weekly_rating_trend", [])
    comparison = data.get("report_comparison", {})
    series_start = trend[0].get("week") if trend else None
    series_end = trend[-1].get("week") if trend else None
    period_class = f" ri-period-grid-{scope}" if scope else ""
    panel(
        f'<div class="ri-period-grid{period_class}">'
        '<div><div class="ri-period-label">Reporting window</div>'
        f'<div class="ri-period-value">{_window(series_start, series_end)}</div></div>'
        '<div><div class="ri-period-label">Four-week comparison</div>'
        f'<div class="ri-period-value">'
        f'{_window(comparison.get("report_start"), comparison.get("report_end"))}'
        "</div></div>"
        '<div><div class="ri-period-label">Source label</div>'
        f'<div class="ri-period-value">{_get(data, "meta", "sample_label", "Report data")}</div></div>'
        "</div>"
    )


def _render_overview_summary(data: dict[str, Any]) -> None:
    comparison = data.get("report_comparison", {})
    previous = comparison.get("previous_four_weeks", {})
    recent = comparison.get("recent_four_weeks", {})
    prev_avg = previous.get("average_rating", 0)
    recent_avg = recent.get("average_rating", 0)
    total = _kpi_value(data, "Total reviews analysed")
    themes = _kpi_value(data, "Discovered themes")
    scope = f" across {total} unique classified reviews" if total != "—" else ""
    delta = recent_avg - prev_avg
    if abs(delta) < 0.001:
        insight = f"{prev_avg:.2f} → {recent_avg:.2f} (unchanged)"
    else:
        movement = "decline" if delta < 0 else "increase"
        insight = f"{prev_avg:.2f} → {recent_avg:.2f} ({abs(delta):.2f}-point {movement})"
    panel(
        '<div class="ri-summary">'
        f'Recent four weeks: {recent.get("reviews", 0):,} reviews at {recent_avg:.2f}/5, '
        f'{_rating_movement(prev_avg, recent_avg)} from the prior four weeks. '
        f"{themes} themes identified{scope}."
        "</div>"
        f'<div class="ri-summary-insight">{insight}</div>'
    )


def _render_volume_summary(data: dict[str, Any]) -> None:
    volume = _get(data, "trends", "weekly_volume", [])
    if not volume:
        caption("No volume data available.")
        return
    total = sum(row.get("reviews", 0) for row in volume)
    cap = max(row.get("reviews", 0) for row in volume)
    panel(
        '<div class="ri-period-grid">'
        '<div><div class="ri-period-label">Reviews included in analysis</div>'
        f'<div class="ri-period-value">{total:,}</div></div>'
        '<div><div class="ri-period-label">Weekly coverage</div>'
        f'<div class="ri-period-value">{len(volume)} weeks</div></div>'
        '<div><div class="ri-period-label">Weekly sampling cap</div>'
        f'<div class="ri-period-value">{cap:,} reviews</div></div>'
        "</div>"
    )
    caption(
        "Boundary weeks may contain fewer reviews because the analysis covers a rolling 12-week period."
    )


def _render_theme_distribution(data: dict[str, Any], *, height: int = 330) -> None:
    themes = [
        row
        for row in data.get("themes", [])
        if isinstance(row, dict)
    ]
    if not themes:
        caption("No theme data available.")
        return

    themes.sort(
        key=lambda row: (
            _as_float(row.get("percentage", 0)),
            _as_float(row.get("count", 0)),
        ),
        reverse=True,
    )
    labels = [f'{row.get("id", "")} · {row.get("name", "")}' for row in themes]
    percentages = [_as_float(row.get("percentage", 0)) for row in themes]
    display = [
        f'{_as_float(row.get("count", 0)):,.0f} reviews · {_as_float(row.get("percentage", 0)):.1f}%'
        for row in themes
    ]
    customdata = [
        [_as_float(row.get("count", 0)), _as_float(row.get("percentage", 0))]
        for row in themes
    ]
    total = sum(_as_float(row.get("count", 0)) for row in themes)
    axis_max = min(100, max(10, int(max(percentages) // 10 + 1) * 10))
    tick_step = 10 if axis_max <= 60 else 20

    figure = horizontal_bar_chart(
        labels,
        percentages,
        title="Share of reviews by theme",
        color=PALETTE["teal"],
        height=height,
        text_template="%{text}",
    )
    figure.data[0].text = display
    figure.data[0].customdata = customdata
    figure.data[0].cliponaxis = False
    figure.data[0].textposition = "outside"
    figure.data[0].hovertemplate = (
        "%{y}<br>Reviews: %{customdata[0]:,.0f}<br>Share: %{customdata[1]:.1f}%<extra></extra>"
    )
    figure.update_layout(margin={"l": 320, "r": 165, "t": 44, "b": 58})
    figure.update_xaxes(
        title_text="Share of reviews (%)",
        range=[0, axis_max],
        tick0=0,
        dtick=tick_step,
        tickformat=".0f%",
    )
    figure.update_yaxes(automargin=True, ticklabelstandoff=8)
    chart(figure)
    caption(
        f"Total analysed sample: {total:,.0f} reviews. "
        "Bars show percentage share; labels show review count and share."
    )


def _render_customer_feedback_themes(data: dict[str, Any]) -> None:
    themes = [row for row in data.get("themes", []) if isinstance(row, dict)]
    if not themes:
        caption("No theme data available.")
        return

    pain_names = {
        str(row.get("category", ""))
        for row in data.get("pain_points", [])
        if isinstance(row, dict)
    }
    pain_ids = {
        str(row.get("id", ""))
        for row in themes
        if str(row.get("name", "")) in pain_names
    }
    ordered = sorted(
        themes,
        key=lambda row: (
            _as_float(row.get("count", 0)),
            _as_float(row.get("percentage", 0)),
        ),
        reverse=True,
    )
    rows = []
    for rank, row in enumerate(ordered, start=1):
        name = str(row.get("name", ""))
        theme_id = str(row.get("id", ""))
        theme_label = escape(f"{theme_id} – {name}")
        is_pain = name in pain_names or theme_id in pain_ids
        classification = "Customer pain point" if is_pain else "Positive signal"
        tone = "medium" if is_pain else "positive"
        row_style = ' style="background: var(--ri-accent-soft);"' if not is_pain else ""
        rows.append(
            f"<tr{row_style}>"
            f'<td class="ri-compare-num">{rank}</td>'
            f"<td>{theme_label}</td>"
            f'<td class="ri-compare-num">{_as_float(row.get("count", 0)):,.0f}</td>'
            f'<td class="ri-compare-num">{_as_float(row.get("percentage", 0)):.1f}%</td>'
            f"<td>{escape(str(row.get('description', '')))}</td>"
            f"<td>{badge(classification, tone)}</td>"
            "</tr>"
        )

    total = sum(_as_float(row.get("count", 0)) for row in ordered)
    share_total = sum(_as_float(row.get("percentage", 0)) for row in ordered)
    panel(
        '<table class="ri-compare" style="table-layout: fixed;">'
        "<colgroup>"
        '<col style="width: 7%;">'
        '<col style="width: 25%;">'
        '<col style="width: 10%;">'
        '<col style="width: 9%;">'
        '<col style="width: 32%;">'
        '<col style="width: 17%;">'
        "</colgroup>"
        "<thead><tr>"
        '<th class="ri-compare-num">Rank</th>'
        "<th>Theme</th>"
        '<th class="ri-compare-num">Reviews</th>'
        '<th class="ri-compare-num">Share</th>'
        "<th>Customer feedback summary</th>"
        "<th>Classification</th>"
        f"</tr></thead><tbody>{''.join(rows)}</tbody></table>"
    )
    caption(
        f"Total: {total:,.0f} reviews across {len(ordered)} themes; "
        f"listed shares total {share_total:.1f}%."
    )


def _concise_positive_description(description: Any) -> str:
    text = str(description or "").strip()
    prefix = "Positive feedback on "
    if text.lower().startswith(prefix.lower()):
        text = text[len(prefix) :]
    text = text.rstrip(" .")
    return f"{text[0].upper()}{text[1:]}" if text else "No description available."


def _render_positive_feedback(data: dict[str, Any]) -> None:
    positive = next(
        (
            row
            for row in data.get("themes", [])
            if isinstance(row, dict) and row.get("id") == "T5"
        ),
        None,
    )
    if not positive:
        caption("No positive feedback theme available.")
        return

    theme_label = escape(f'{positive.get("id", "")} · {positive.get("name", "")}')
    count = _as_float(positive.get("count", 0))
    percentage = _as_float(positive.get("percentage", 0))
    description = escape(_concise_positive_description(positive.get("description", "")))
    panel(
        '<div style="border-left: 3px solid var(--ri-accent); padding-left: 1rem;">'
        '<div style="display: flex; align-items: center; justify-content: space-between; gap: 0.75rem;">'
        f'<div class="ri-period-label">{theme_label}</div>'
        f'{badge("Positive signal", "positive")}'
        "</div>"
        f'<div class="ri-kpi-value">{count:,.0f} reviews</div>'
        f'<div class="ri-summary-insight">{percentage:.1f}% of the analysed sample</div>'
        f'<div class="ri-summary">{description}</div>'
        "</div>"
    )


def _render_recommendation_cards(
    recommendations: list[dict[str, Any]],
    *,
    concise: bool = False,
) -> None:
    if not recommendations:
        caption("No recommendations listed.")
        return

    for row in recommendations:
        priority = str(row.get("priority", "Neutral"))
        evidence = str(row.get("evidence", ""))
        if concise:
            evidence = _concise_evidence(evidence)
        st.markdown(
            '<article class="ri-recommendation-card">'
            '<div class="ri-recommendation-head">'
            "<div>"
            '<div class="ri-recommendation-eyebrow">Identified problem</div>'
            f'<div class="ri-recommendation-title">{escape(str(row.get("problem", "")))}</div>'
            "</div>"
            '<div class="ri-recommendation-badge">'
            f'{badge(f"Illustrative priority: {escape(priority)}", _tone(priority))}'
            "</div>"
            "</div>"
            '<div class="ri-recommendation-body">'
            '<div class="ri-recommendation-field">'
            '<span class="ri-recommendation-label">Supporting evidence:</span> '
            f"<span>{escape(evidence)}</span>"
            "</div>"
            '<div class="ri-recommendation-field ri-recommendation-improvement">'
            '<span class="ri-recommendation-label">Suggested improvement:</span> '
            f'<span>{escape(str(row.get("improvement", "")))}</span>'
            "</div>"
            "</div>"
            "</article>",
            unsafe_allow_html=True,
        )


def _render_product_recommendations(data: dict[str, Any]) -> None:
    st.markdown(
        '<div class="ri-recommendation-note">Suggested priorities are illustrative and '
        "have not been validated through a formal prioritisation exercise.</div>",
        unsafe_allow_html=True,
    )
    _render_recommendation_cards(data.get("recommendations", []))


def _as_float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _share(part: Any, total: Any) -> float | None:
    denominator = _as_float(total)
    if denominator <= 0:
        return None
    return _as_float(part) / denominator * 100


def _share_text(value: float | None) -> str:
    return "—" if value is None else f"{value:.1f}%"


def _share_delta(before: float | None, after: float | None) -> float | None:
    if before is None or after is None:
        return None
    return after - before


def _concise_evidence(value: Any) -> str:
    text = str(value or "").strip()
    for prefix in (
        "The weekly pulse highlights ",
        "The weekly pulse reports ",
        "Reviews describe ",
    ):
        if text.lower().startswith(prefix.lower()):
            text = text[len(prefix) :]
            break
    return text.rstrip(" .")


def _comparison_tone(value: float | None) -> str:
    if value is None:
        return "ri-compare-flat"
    if value > 0:
        return "ri-compare-up"
    if value < 0:
        return "ri-compare-down"
    return "ri-compare-flat"


def _render_comparison_table(previous: dict[str, Any], recent: dict[str, Any]) -> None:
    prev_reviews = previous.get("reviews", 0)
    recent_reviews = recent.get("reviews", 0)
    prev_low = previous.get("low_rating", 0)
    recent_low = recent.get("low_rating", 0)
    prev_high = previous.get("high_rating", 0)
    recent_high = recent.get("high_rating", 0)
    prev_avg = previous.get("average_rating", 0)
    recent_avg = recent.get("average_rating", 0)
    prev_low_share = _share(prev_low, prev_reviews)
    recent_low_share = _share(recent_low, recent_reviews)
    prev_high_share = _share(prev_high, prev_reviews)
    recent_high_share = _share(recent_high, recent_reviews)

    rows = [
        ("Reviews", f"{prev_reviews:,}", f"{recent_reviews:,}", recent_reviews - prev_reviews, "count"),
        ("Average rating", f"{prev_avg:.2f} / 5", f"{recent_avg:.2f} / 5", recent_avg - prev_avg, "rating"),
        ("Low-rating reviews", f"{prev_low:,}", f"{recent_low:,}", recent_low - prev_low, "count"),
        ("High-rating reviews", f"{prev_high:,}", f"{recent_high:,}", recent_high - prev_high, "count"),
        (
            "Low-rating share of total reviews",
            _share_text(prev_low_share),
            _share_text(recent_low_share),
            _share_delta(prev_low_share, recent_low_share),
            "share",
        ),
        (
            "High-rating share of total reviews",
            _share_text(prev_high_share),
            _share_text(recent_high_share),
            _share_delta(prev_high_share, recent_high_share),
            "share",
        ),
    ]

    rendered_rows = []
    for label, before, after, delta, kind in rows:
        if delta is None:
            delta_text = "—"
        elif kind == "count":
            delta_text = f"{delta:+,}"
        elif kind == "share":
            delta_text = f"{delta:+.1f} pp"
        else:
            delta_text = f"{delta:+.2f}"
        rendered_rows.append(
            f"<tr><td>{label}</td>"
            f'<td class="ri-compare-num">{before}</td>'
            f'<td class="ri-compare-num">{after}</td>'
            f'<td class="ri-compare-num {_comparison_tone(delta)}">{delta_text}</td></tr>'
        )

    panel(
        '<table class="ri-compare"><thead><tr>'
        "<th>Metric</th>"
        '<th class="ri-compare-num">Previous 4 weeks</th>'
        '<th class="ri-compare-num">Recent 4 weeks</th>'
        '<th class="ri-compare-num">Change</th>'
        f"</tr></thead><tbody>{''.join(rendered_rows)}</tbody></table>"
    )
    caption(
        "Low- and high-rating shares use each period's total review count as the denominator, "
        "including 3-star reviews. A smaller review count is not treated as an improvement on its own."
    )


def render_overview_section(data: dict[str, Any]) -> None:
    section_title("Executive dashboard")
    kpi_row(_get(data, "overview", "kpis", []), scope="overview")

    section_title("Executive summary")
    _render_overview_summary(data)

    section_title("Reporting period and analysis coverage")
    _render_reporting_period(data)

    section_title("Weekly rating trend")
    trend = _get(data, "overview", "weekly_rating_trend", [])
    if trend:
        chart(
            rating_trend_chart(
                [row["week"] for row in trend],
                [row["rating"] for row in trend],
                title="Average rating by week",
                y_title="Rating (out of 5)",
            )
        )
    else:
        caption("No weekly trend data available.")


def _render_weekly_rating_summary(ratings: list[dict[str, Any]], volume: list[dict[str, Any]]) -> None:
    points = [
        (str(row.get("week", "")), _as_float(row.get("rating")))
        for row in ratings
        if row.get("week") is not None
    ]
    if not points:
        caption("No rating summary available.")
        return
    highest = max(points, key=lambda item: item[1])
    lowest = min(points, key=lambda item: item[1])
    latest = points[-1]
    week_counts = {row.get("week"): _as_float(row.get("reviews")) for row in volume}
    cap = max(week_counts.values()) if week_counts else 0.0
    latest_count = week_counts.get(latest[0])
    partial = latest_count is not None and cap > 0 and latest_count < cap
    latest_suffix = " (partial week)" if partial else ""
    panel(
        '<div class="ri-period-grid">'
        '<div><div class="ri-period-label">Highest weekly rating</div>'
        f'<div class="ri-period-value">{highest[1]:.2f} · {_format_date(highest[0])}</div></div>'
        '<div><div class="ri-period-label">Lowest weekly rating</div>'
        f'<div class="ri-period-value">{lowest[1]:.2f} · {_format_date(lowest[0])}</div></div>'
        '<div><div class="ri-period-label">Latest weekly rating</div>'
        f'<div class="ri-period-value">{latest[1]:.2f} · {_format_date(latest[0])}{latest_suffix}</div></div>'
        "</div>"
    )
    if partial and latest_count is not None:
        caption(
            f"The latest week includes {int(latest_count):,} reviews against a {int(cap):,}-review "
            "weekly cap, so it is a partial boundary week."
        )


def _rating_split_figure(
    split: list[dict[str, Any]], volume: list[dict[str, Any]]
) -> Any:
    figure = stacked_bar_chart(
        [row["week"] for row in split],
        {
            "Low-rating reviews (1–2 stars)": [row["low"] for row in split],
            "High-rating reviews (4–5 stars)": [row["high"] for row in split],
        },
        title="High-rating versus low-rating reviews",
        colors=[PALETTE["red"], PALETTE["teal"]],
        y_title="Reviews included",
    )
    week_counts = {row.get("week"): _as_float(row.get("reviews")) for row in volume}
    for trace, key in zip(figure.data, ("low", "high")):
        percentages = [
            _share(row.get(key), week_counts.get(row.get("week"), 0)) or 0.0 for row in split
        ]
        trace.customdata = percentages
        trace.hovertemplate = (
            "%{x}<br>"
            + str(trace.name)
            + ": %{y:,} (%{customdata:.1f}% of weekly reviews)<extra></extra>"
        )
    return figure


def render_weekly_pulse_section(data: dict[str, Any]) -> None:
    comparison = data.get("report_comparison", {})
    previous = comparison.get("previous_four_weeks", {})
    recent = comparison.get("recent_four_weeks", {})
    prev_avg = previous.get("average_rating", 0)
    recent_avg = recent.get("average_rating", 0)

    section_title("Executive summary")
    panel(
        '<div class="ri-summary">'
        f'Recent four weeks ({_window(comparison.get("report_start"), comparison.get("report_end"))}): '
        f'{recent.get("reviews", 0):,} reviews at {recent_avg:.2f}/5, '
        f'{_rating_movement(prev_avg, recent_avg)} from the prior four weeks ({prev_avg:.2f}/5). '
        f'High-rating reviews moved from {previous.get("high_rating", 0):,} to '
        f'{recent.get("high_rating", 0):,}; low-rating reviews moved from '
        f'{previous.get("low_rating", 0):,} to {recent.get("low_rating", 0):,}.'
        "</div>"
    )

    section_title("Included reviews summary")
    _render_volume_summary(data)

    section_title("Previous 4 weeks vs recent 4 weeks comparison table")
    _render_comparison_table(previous, recent)

    section_title("Reviews included in analysis per week")
    volume = _get(data, "trends", "weekly_volume", [])
    if volume:
        cap = max(row.get("reviews", 0) for row in volume)
        chart(
            bar_chart(
                [row["week"] for row in volume],
                [row["reviews"] for row in volume],
                title="Reviews included in analysis per week",
                y_title="Reviews included",
            )
        )
        caption(
            f"Balanced dataset; maximum {cap:,} reviews per week. "
            f"The {cap:,}-review ceiling is the weekly sampling cap and should not be "
            "interpreted as the actual peak in Play Store review submissions."
        )
    else:
        caption("No volume data available.")

    section_title("Weekly average rating trend")
    ratings = _get(data, "trends", "rating_trend", [])
    if ratings:
        _render_weekly_rating_summary(ratings, volume)
        chart(
            line_chart(
                [row["week"] for row in ratings],
                [row["rating"] for row in ratings],
                "Average rating",
                title="Weekly average rating",
                color=PALETTE["blue"],
                y_title="Rating (out of 5)",
            )
        )
    else:
        caption("No rating trend data available.")

    section_title("High-rating and low-rating reviews by week")
    split = _get(data, "trends", "rating_split", [])
    if split:
        chart(_rating_split_figure(split, volume))
        caption(
            "This comparison covers only low-rating (1–2 star) and high-rating (4–5 star) "
            "reviews; 3-star reviews are excluded. It is not the complete rating distribution. "
            "Percentages in the chart tooltip use each week's total included reviews as the denominator."
        )
    else:
        caption("No rating split data available.")


def render_product_insights_section(data: dict[str, Any]) -> None:
    section_title("Customer feedback distribution")
    _render_theme_distribution(data)

    section_title("Customer Feedback Themes & Pain Points")
    _render_customer_feedback_themes(data)

    section_title("What customers appreciate")
    _render_positive_feedback(data)

    section_title("Recommended product improvements")
    _render_product_recommendations(data)


def _approved_claim_count(fact_check: list[dict[str, Any]]) -> int:
    for row in fact_check:
        if not isinstance(row, dict):
            continue
        status = str(row.get("status", ""))
        if "approved" not in status.lower():
            continue
        for token in status.replace(",", " ").split():
            if token.isdigit():
                return int(token)
    return 0


def _first_text(record: dict[str, Any], keys: tuple[str, ...]) -> str:
    for key in keys:
        value = record.get(key)
        if value not in (None, ""):
            text = str(value).strip()
            if text:
                return text
    return ""


def _fee_classification_rows(
    fees: dict[str, Any], *, sample_size: int
) -> list[dict[str, Any]]:
    classification = fees.get("classification") or []
    if isinstance(classification, dict):
        entries: list[Any] = [
            {"category": category, "count": count}
            for category, count in classification.items()
        ]
    elif isinstance(classification, list):
        entries = classification
    else:
        return []

    rows: list[dict[str, Any]] = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        category = _first_text(entry, ("category", "name", "label", "theme"))
        raw_count = next(
            (
                entry.get(key)
                for key in ("count", "mentions", "reviews", "review_count")
                if entry.get(key) not in (None, "")
            ),
            None,
        )
        if not category or raw_count is None:
            continue
        try:
            count = float(raw_count)
        except (TypeError, ValueError):
            continue
        raw_share = next(
            (
                entry.get(key)
                for key in ("percentage", "share", "pct")
                if entry.get(key) not in (None, "")
            ),
            None,
        )
        share = (
            _as_float(raw_share)
            if raw_share is not None
            else ((count / sample_size * 100) if sample_size else 0.0)
        )
        rows.append({"category": category, "count": count, "share": share})
    rows.sort(key=lambda row: row["count"], reverse=True)
    return rows


def _approved_claim_records(fees: dict[str, Any]) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    wording_keys = ("claim", "claim_text", "wording", "text", "title")
    explanation_keys = ("explanation", "description", "detail", "summary")
    status_keys = ("status", "verification_status", "verification")
    source_keys = ("source", "source_reference", "reference", "url", "source_url")
    notes_keys = ("notes", "evidence", "evidence_notes")

    def add_record(entry: dict[str, Any], fallback_status: str = "") -> None:
        title = _first_text(entry, wording_keys)
        if not title:
            return
        record = {"title": title}
        for field, keys in (
            ("explanation", explanation_keys),
            ("status", status_keys),
            ("source", source_keys),
            ("notes", notes_keys),
        ):
            value = _first_text(entry, keys)
            if value:
                record[field] = value
        if "status" not in record and fallback_status:
            record["status"] = fallback_status
        records.append(record)

    for key in ("approved_claims", "approved_fee_claims"):
        entries = fees.get(key) or []
        if not isinstance(entries, list):
            continue
        for entry in entries:
            if isinstance(entry, str):
                add_record({"claim": entry}, "Approved")
            else:
                add_record(entry, "Approved")

    for row in fees.get("fact_check", []) or []:
        if not isinstance(row, dict):
            continue
        status = _first_text(row, status_keys)
        if "approved" not in status.lower():
            continue
        add_record(row, status)

    for claim in APPROVED_FEE_CLAIMS:
        add_record({"claim": claim}, "Approved")
    return records


def render_fee_explainer_section(data: dict[str, Any]) -> None:
    fees = data.get("fee_analysis", {}) or {}
    pilot_size = int(fees.get("pilot_sample_size", 0) or 0)
    related_count = int(fees.get("fee_related_review_count", 0) or 0)
    fact_check = fees.get("fact_check", []) or []
    approved_count = _approved_claim_count(fact_check)
    claim_records = _approved_claim_records(fees)
    not_classified = max(related_count - pilot_size, 0)
    coverage = (pilot_size / related_count * 100) if related_count else 0.0
    overview_note = (
        f"Only {pilot_size:,} of the {related_count:,} fee-related reviews were included in the "
        "classification pilot. The classification results are provisional and do not represent "
        "the complete fee-related review dataset."
    )

    section_title("Fee-related review overview")
    coverage_metrics = [
        ("Identified fee-related reviews", f"{related_count:,}"),
        ("Classified pilot reviews", f"{pilot_size:,}"),
        ("Not yet classified", f"{not_classified:,}"),
        ("Pilot coverage", f"{coverage:.1f}%"),
    ]
    coverage_html = "".join(
        '<div class="ri-fee-coverage-item">'
        f'<div class="ri-fee-coverage-label">{escape(label)}</div>'
        f'<div class="ri-fee-coverage-value">{escape(value)}</div>'
        "</div>"
        for label, value in coverage_metrics
    )
    panel(
        f'<div class="ri-fee-coverage-grid">{coverage_html}</div>'
        '<div class="ri-fee-progress">'
        '<div class="ri-fee-progress-head"><span>Pilot coverage</span>'
        f"<strong>{coverage:.1f}%</strong></div>"
        '<div class="ri-fee-progress-track" role="progressbar" aria-label="Classification pilot coverage" '
        f'aria-valuenow="{coverage:.1f}" aria-valuemin="0" aria-valuemax="100">'
        f'<div class="ri-fee-progress-fill" style="width: {coverage:.1f}%"></div>'
        "</div></div>"
        f'<div class="ri-fee-scope-note">{escape(overview_note)}</div>'
    )

    section_title("Customer fee concerns")
    classification_rows = _fee_classification_rows(fees, sample_size=pilot_size)
    if classification_rows:
        labels = [row["category"] for row in classification_rows]
        counts = [row["count"] for row in classification_rows]
        shares = [row["share"] for row in classification_rows]
        display = [
            f'{count:,.0f} reviews · {share:.1f}%'
            for count, share in zip(counts, shares)
        ]
        customdata = [[count, share] for count, share in zip(counts, shares)]
        axis_max = min(100, max(10, int(max(shares) // 10 + 1) * 10))
        figure = horizontal_bar_chart(
            labels,
            shares,
            title="Fee concern categories in classification pilot",
            color=PALETTE["teal"],
            height=330,
            text_template="%{text}",
        )
        figure.data[0].text = display
        figure.data[0].customdata = customdata
        figure.data[0].hovertemplate = (
            "%{y}<br>Reviews: %{customdata[0]:,.0f}<br>Share of pilot: %{customdata[1]:.1f}%<extra></extra>"
        )
        figure.update_layout(margin={"l": 280, "r": 130, "t": 44, "b": 58})
        figure.update_xaxes(
            title_text="Share of pilot reviews (%)",
            range=[0, axis_max],
            tick0=0,
            dtick=10 if axis_max <= 60 else 20,
            tickformat=".1f%",
        )
        figure.update_yaxes(automargin=True, ticklabelstandoff=8)
        chart(figure)
        caption(
            f"Classification sample: {pilot_size:,} reviews. This breakdown represents only the "
            f"{pilot_size:,}-review pilot, not all {related_count:,} fee-related reviews."
        )
    else:
        panel(
            '<div class="ri-fee-empty">'
            '<div class="ri-fee-empty-mark" aria-hidden="true">i</div>'
            "<div>"
            '<div class="ri-fee-empty-title">Category-level pilot results are not available</div>'
            '<div class="ri-fee-empty-detail">The dashboard payload does not include category-level '
            "counts for the fee classification pilot. No chart, categories or counts have been invented.</div>"
            "</div></div>"
        )

    section_title("Fee explanations")
    fact_result_html = (
        '<div class="ri-fee-result">'
        '<div class="ri-fee-empty-mark" aria-hidden="true">✓</div>'
        '<div class="ri-fee-result-copy">'
        '<div class="ri-fee-result-kicker">FACT-CHECK RESULT</div>'
        f'<div class="ri-fee-result-value">{approved_count:,}</div>'
        '<div class="ri-fee-result-label">fee claims passed the existing fact-check</div>'
        "</div></div>"
    )
    if claim_records:
        claim_html = "".join(
            '<article class="ri-fee-claim-card">'
            f'<div class="ri-fee-claim-id">C{index:02d}</div>'
            f'<div class="ri-fee-claim-wording">{escape(record["title"])}</div>'
            + (
                f'<div class="ri-fee-empty-detail">{escape(record["explanation"])}</div>'
                if record.get("explanation")
                else ""
            )
            + (
                '<div class="ri-fee-claim-verification"><span class="ri-badge ri-badge-positive">'
                f'{escape(record["status"])}</span></div>'
                if record.get("status")
                else ""
            )
            + (
                f'<div class="ri-fee-claim-source">Source: {escape(record["source"])}</div>'
                if record.get("source")
                else ""
            )
            + (
                f'<div class="ri-fee-claim-source">Notes: {escape(record["notes"])}</div>'
                if record.get("notes")
                else ""
            )
            + "</article>"
            for index, record in enumerate(claim_records, start=1)
        )
        panel(f'{fact_result_html}<div class="ri-fee-claim-grid">{claim_html}</div>')
    else:
        fact_rows = "".join(
            '<div class="ri-fee-note">'
            f"<strong>{escape(_first_text(row, ('item', 'claim', 'title')) or 'Fact-check record')}</strong>"
            f" — {escape(_first_text(row, ('status', 'verification_status', 'verification')))}"
            "</div>"
            for row in fact_check
            if isinstance(row, dict)
            and not any(
                token.isdigit() and int(token) == approved_count
                for token in _first_text(row, ("status", "verification_status", "verification"))
                .replace(",", " ")
                .split()
            )
        )
        panel(
            f'{fact_result_html}'
            '<div class="ri-fee-empty">'
            '<div class="ri-fee-empty-mark" aria-hidden="true">i</div>'
            "<div>"
            '<div class="ri-fee-empty-title">Individual claim details are not available</div>'
            '<div class="ri-fee-empty-detail">Individual claim wording, explanations, evidence or notes are '
            "not included in the dashboard payload. Only the aggregate fact-check outcome is shown; these are "
            "claim verifications, not classified customer reviews."
            f"{fact_rows}</div>"
            "</div></div>"
        )

    section_title("Fact-check process")
    process_steps = [
        (
            "01",
            "Identify fee-related information",
            '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 6h14M5 12h9M5 18h6"/></svg>',
        ),
        (
            "02",
            "Retrieve official Groww pricing information",
            '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="8"/>'
            '<path d="M4 12h16M12 4c2.2 2.2 3.3 4.9 3.3 8S14.2 17.8 12 20c-2.2-2.2-3.3-4.9-3.3-8S9.8 6.2 12 4z"/></svg>',
        ),
        (
            "03",
            "Compare claims against official sources",
            '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 5h7v14H4zM13 5h7v14h-7z"/>'
            '<path d="M7 9h1M16 9h1M7 13h1M16 13h1"/></svg>',
        ),
        (
            "04",
            "Run the fact-check",
            '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3l7 3v5c0 4.1-2.9 7.4-7 9-4.1-1.6-7-4.9-7-9V6l7-3z"/>'
            '<path d="M9 12l2 2 4-4"/></svg>',
        ),
        (
            "05",
            "Display the verification outcome",
            '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="8"/>'
            '<path d="M8.5 12.2l2.3 2.3 4.7-5"/></svg>',
        ),
    ]
    process_html = "".join(
        '<div class="ri-fee-process-step">'
        '<div class="ri-fee-process-top">'
        f'<span class="ri-fee-process-icon">{icon}</span>'
        f'<span class="ri-fee-process-number">STEP {number}</span>'
        "</div>"
        f'<div class="ri-fee-process-label">{escape(label)}</div>'
        "</div>"
        for number, label, icon in process_steps
    )
    st.markdown(f'<div class="ri-fee-process">{process_html}</div>', unsafe_allow_html=True)
    caption(
        "This sequence reflects the existing analysis workflow. The Streamlit page presents recorded "
        "outcomes and does not run fact-checks independently."
    )

    section_title("Official sources")
    source_details = {
        "https://groww.in/pricing": (
            "Groww Official Pricing Page",
            "Official pricing reference for brokerage and account-related charges.",
        ),
        "https://groww.in/help/payments-%26-withdrawals/payments-charges/apart-from-brokerage--what-fees-am-i-charged--93": (
            "Groww Official Charges Help Article",
            "Official help article explaining charges beyond brokerage.",
        ),
    }
    sources = fees.get("sources", []) or []
    source_cards = []
    for row in sources:
        if not isinstance(row, dict):
            continue
        url = _first_text(row, ("url", "link", "href"))
        if not url:
            continue
        fallback_title, fallback_detail = source_details.get(url, (url, "Official Groww reference."))
        title = _first_text(row, ("label", "title", "name")) or fallback_title
        description = _first_text(row, ("description", "detail", "summary")) or fallback_detail
        last_checked = _first_text(
            row, ("last_checked", "last_checked_date", "checked_on", "checked_at")
        )
        checked_html = (
            f'<div class="ri-fee-claim-source">Last checked: {escape(last_checked)}</div>'
            if last_checked
            else ""
        )
        source_cards.append(
            '<article class="ri-fee-source-card">'
            '<div class="ri-fee-source-kicker">OFFICIAL REFERENCE</div>'
            f'<div class="ri-fee-source-title">{escape(title)}</div>'
            f'<div class="ri-fee-source-detail">{escape(description)}</div>'
            f"{checked_html}"
            f'<a class="ri-fee-source-link" href="{escape(url)}" target="_blank" rel="noopener noreferrer">'
            "Open source ↗</a>"
            "</article>"
        )
    if source_cards:
        panel(f'<div class="ri-fee-source-grid">{"".join(source_cards)}</div>')
    else:
        panel(
            '<div class="ri-fee-empty">'
            '<div class="ri-fee-empty-mark" aria-hidden="true">i</div>'
            "<div>"
            '<div class="ri-fee-empty-title">Official sources are not included</div>'
            '<div class="ri-fee-empty-detail">No official source references are available in the current '
            "dashboard payload, so no links are shown.</div>"
            "</div></div>"
        )

    section_title("Evidence and limitations")
    limitations = [
        (
            "Review classification",
            f"Only {pilot_size:,} of {related_count:,} fee-related reviews were classified in the pilot.",
        ),
        (
            "Provisional findings",
            "Classification findings are provisional and do not represent the complete fee-related review dataset.",
        ),
        (
            "Claim verification",
            "Only the aggregate fact-check outcome is available in the dashboard payload.",
        ),
        (
            "Official references",
            "Official Groww pricing and help sources were used for verification.",
        ),
    ]
    limitation_html = "".join(
        '<article class="ri-limitation-card">'
        f'<div class="ri-limitation-label">{escape(label)}</div>'
        f'<div class="ri-limitation-detail">{escape(detail)}</div>'
        "</article>"
        for label, detail in limitations
    )
    panel(f'<div class="ri-limitation-grid">{limitation_html}</div>')


def render_data_quality_section(data: dict[str, Any]) -> None:
    records = load_validation_records(data)
    counts = summarise_counts(records)
    area_rows = summarise_areas(records)
    source_labels = {
        "data_quality_report.md": "Quality report",
        "reviews_for_analysis.csv": "Full analysis CSV",
        "reviews_balanced_for_analysis.csv": "Balanced analysis CSV",
        "report.json": "Dashboard payload",
    }
    display_labels = {
        "data_quality_report.md": "quality report",
        "reviews_for_analysis.csv": "full analysis dataset",
        "reviews_balanced_for_analysis.csv": "balanced analysis dataset",
        "groww_reviews_cleaned.csv": "source review data",
        "groww_reviews_balanced.csv": "balanced source data",
        "build_guide_csv_validation.md": "historical validation report",
        "report.json": "dashboard payload",
    }
    fees = data.get("fee_analysis", {}) or {}
    related_count = fees.get("fee_related_review_count", 0)
    pilot_size = fees.get("pilot_sample_size", 0)
    result_tones = {
        "Pass": "pass",
        "Fail": "fail",
        "Warning": "warning",
        "Not available": "neutral",
    }

    def result_badge(result: str) -> str:
        tone = result_tones.get(result, "neutral")
        return f'<span class="ri-validation-result ri-validation-result-{tone}">{escape(result)}</span>'

    def source_label(source: str) -> str:
        return source_labels.get(source, "Validation source")

    def display_text(value: str) -> str:
        text = value
        for token, label in display_labels.items():
            text = text.replace(token, label)
        return text

    def summary_card(label: str, value: int, note: str, tone: str) -> str:
        return (
            f'<div class="ri-validation-summary-card ri-validation-summary-{tone}">'
            f'<div class="ri-validation-summary-label">{escape(label)}</div>'
            f'<div class="ri-validation-summary-value">{value}</div>'
            f'<div class="ri-validation-summary-note">{escape(note)}</div>'
            "</div>"
        )

    section_title("Checks summary")
    st.markdown(
        '<div class="ri-validation-summary">'
        + summary_card("Total checks", counts["total"], f"{len(area_rows)} areas checked", "neutral")
        + summary_card("Passed checks", counts["passed"], "Evidence recorded", "pass")
        + summary_card("Failed checks", counts["failed"], "Needs attention", "fail")
        + summary_card("Warnings", counts["warnings"], "Limited coverage", "warning")
        + "</div>",
        unsafe_allow_html=True,
    )

    area_html = "".join(
        '<tr>'
        f'<td data-label="Area"><span class="ri-validation-area">{escape(row["area"])}</span></td>'
        f'<td data-label="Result">{result_badge(row["result"])}</td>'
        f'<td data-label="Check">{escape(display_text(row["check"]))}</td>'
        "</tr>"
        for row in area_rows
    )
    section_title("Validation results")
    st.markdown(
        '<div class="ri-validation-table-wrap">'
        '<table class="ri-validation-table">'
        "<thead><tr><th>Area</th><th>Result</th><th>Check</th></tr></thead>"
        f"<tbody>{area_html}</tbody>"
        "</table>"
        "</div>",
        unsafe_allow_html=True,
    )

    with st.expander("Full Validation Report", expanded=False):
        detail_html = "".join(
            "<tr>"
            f'<td data-label="Area">{escape(record["area"])}</td>'
            f'<td data-label="Result">{result_badge(record["result"])}</td>'
            f'<td data-label="Check">{escape(display_text(record["check"]))}</td>'
            f'<td data-label="Detail">{escape(display_text(record["detail"]))}</td>'
            f'<td data-label="Source">{escape(source_label(record["source"]))}</td>'
            "</tr>"
            for record in records
        )
        st.markdown(
            '<div class="ri-validation-table-wrap ri-validation-detail-wrap">'
            '<table class="ri-validation-table ri-validation-detail-table">'
            "<thead><tr><th>Area</th><th>Result</th><th>Check</th><th>Detail</th><th>Source</th></tr></thead>"
            f"<tbody>{detail_html}</tbody>"
            "</table>"
            "</div>",
            unsafe_allow_html=True,
        )

    limitations = [
        ("Review text", "No verbatim review text in the dashboard payload."),
        (
            "Fee pilot scope",
            f"Only {pilot_size} of {related_count} fee-related reviews classified; findings are provisional.",
        ),
        ("Severity", "Pain point severity not assessed."),
        (
            "Theme taxonomy",
            "T1–T5 are analytical groupings, not official product taxonomy.",
        ),
    ]
    limitation_html = "".join(
        '<div class="ri-limitation-card">'
        '<div class="ri-limitation-label">Limitation</div>'
        f'<div class="ri-limitation-title">{escape(title)}</div>'
        f'<div class="ri-limitation-detail">{escape(detail)}</div>'
        "</div>"
        for title, detail in limitations
    )
    section_title("Analysis limitations")
    st.markdown(f'<div class="ri-limitation-grid">{limitation_html}</div>', unsafe_allow_html=True)


def render_how_it_works_section(data: dict[str, Any]) -> None:
    section_title("End-to-end workflow")
    steps = []
    for step in PIPELINE_STEPS:
        outputs = "".join(
            f'<span class="ri-step-output">{escape(output)}</span>'
            for output in step["outputs"]
        )
        output_html = (
            f'<div class="ri-step-outputs">{outputs}</div>' if outputs else ""
        )
        steps.append(
            f'<div class="ri-pipeline-step ri-pipeline-step-{step["kind"]}">'
            f'<div class="ri-step-num">{escape(step["number"])}</div>'
            f'<div class="ri-step-title">{escape(step["title"])}</div>'
            f'<div class="ri-step-detail">{escape(step["detail"])}</div>'
            f"{output_html}"
            "</div>"
        )
    top_row = _workflow_connector("right").join(steps[:4])
    bottom_row = _workflow_connector("left").join(steps[4:])
    panel(
        '<div class="ri-pipeline">'
        f'<div class="ri-pipeline-row ri-pipeline-row-top">{top_row}</div>'
        '<div class="ri-pipeline-turn">'
        f'{_workflow_connector("down", "ri-workflow-connector-turn")}'
        "</div>"
        f'<div class="ri-pipeline-row ri-pipeline-row-bottom">{bottom_row}</div>'
        "</div>"
    )

    section_title("Roles in the platform")
    role_columns = st.columns(3)
    for column, (name, role, detail) in zip(role_columns, ROLE_CARDS):
        with column:
            st.markdown(
                '<div class="ri-role-card">'
                f'<div class="ri-role-label">{escape(role)}</div>'
                f'<div class="ri-role-name">{escape(name)}</div>'
                f'<div class="ri-role-detail">{escape(detail)}</div>'
                "</div>",
                unsafe_allow_html=True,
            )

    section_title("Data contract")
    st.markdown(
        '<div class="ri-muted ri-how-data-intro">'
        "The Streamlit layer reads report.json and renders the six Product Intelligence views. "
        "No data is collected, classified or rewritten by the dashboard."
        "</div>",
        unsafe_allow_html=True,
    )
    _render_reporting_period(data, scope="how")
