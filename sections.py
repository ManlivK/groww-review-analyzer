"""Render functions for each dashboard section.

Every renderer takes the report dictionary returned by ``load_report_data``,
which keeps the UI independent of where the data comes from.
"""

from __future__ import annotations

from typing import Any

import streamlit as st

from components.charts import (
    PALETTE,
    bar_chart,
    donut_chart,
    horizontal_bar_chart,
    line_chart,
    stacked_bar_chart,
)
from components.ui import badge, caption, chart, item_card, kpi_row, section_title


def _field(data: dict[str, Any], section: str, key: str, default: Any = None) -> Any:
    return data.get(section, {}).get(key, default)


def _tone_for_severity(severity: str) -> str:
    return {"High": "high", "Medium": "medium", "Low": "low"}.get(severity, "neutral")


def render_overview(data: dict[str, Any]) -> None:
    kpi_row(_field(data, "overview", "kpis", []))

    section_title("Weekly rating trend")
    trend = _field(data, "overview", "weekly_rating_trend", [])
    if trend:
        chart(
            line_chart(
                [row["week"] for row in trend],
                [row["rating"] for row in trend],
                "Average rating",
                title="Average rating by week",
                y_title="Rating (out of 5)",
            )
        )
    else:
        caption("No weekly trend data available.")

    distribution = _field(data, "overview", "feedback_distribution", [])
    opportunities = _field(data, "overview", "opportunities", [])

    if distribution:
        left, right = st.columns([1, 1.25])
        with left:
            section_title("Customer feedback distribution")
            chart(
                donut_chart(
                    [row["label"] for row in distribution],
                    [row["value"] for row in distribution],
                    title="Sentiment split",
                    colors=[row.get("color") for row in distribution],
                )
            )
        opportunity_container = right
    else:
        opportunity_container = st.container()

    with opportunity_container:
        section_title("Key product opportunities")
        if not opportunities:
            caption("No opportunities listed.")
        for opportunity in opportunities:
            st.markdown(
                item_card(
                    title=opportunity.get("title", ""),
                    detail=opportunity.get("detail", ""),
                    badge_text=opportunity.get("impact", ""),
                    badge_tone=_tone_for_severity(opportunity.get("impact", "")),
                ),
                unsafe_allow_html=True,
            )


def render_review_trends(data: dict[str, Any]) -> None:
    section_title("Weekly review volume")
    volume = _field(data, "trends", "weekly_volume", [])
    if volume:
        chart(
            bar_chart(
                [row["week"] for row in volume],
                [row["reviews"] for row in volume],
                title="Reviews received per week",
                y_title="Reviews",
            )
        )
    else:
        caption("No volume data available.")

    left, right = st.columns(2)
    with left:
        section_title("Average rating trend")
        ratings = _field(data, "trends", "rating_trend", [])
        if ratings:
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
    with right:
        section_title("Low-rating versus high-rating reviews")
        split = _field(data, "trends", "rating_split", [])
        if split:
            chart(
                stacked_bar_chart(
                    [row["week"] for row in split],
                    {
                        "Low rating": [row["low"] for row in split],
                        "High rating": [row["high"] for row in split],
                    },
                    title="Rating mix by week",
                    colors=[PALETTE["red"], PALETTE["teal"]],
                    y_title="Reviews",
                )
            )
        else:
            caption("No rating split data available.")


def render_theme_analysis(data: dict[str, Any]) -> None:
    themes = data.get("themes", [])

    left, right = st.columns([1.1, 1])
    with left:
        section_title("T1 to T5 theme distribution")
        if themes:
            chart(
                horizontal_bar_chart(
                    [f'{row["id"]} · {row["name"]}' for row in themes],
                    [row["percentage"] for row in themes],
                    title="Share of reviews by theme",
                    color=PALETTE["teal"],
                    height=365,
                    text_template="%{x:.1f}%",
                )
            )
        else:
            caption("No theme data available.")
    with right:
        section_title("Ranked theme breakdown")
        if themes:
            ranked = sorted(themes, key=lambda row: row.get("count", 0), reverse=True)
            rows = "".join(
                f'<tr><td class="ri-theme-id">{row.get("id", "")}</td>'
                f'<td>{row.get("name", "")}</td>'
                f'<td class="ri-theme-num">{row.get("count", 0):,}</td>'
                f'<td class="ri-theme-num">{row.get("percentage", 0):.1f}%</td></tr>'
                for row in ranked
            )
            st.markdown(
                '<div class="ri-panel ri-theme-table">'
                "<table><thead><tr>"
                "<th>Theme ID</th><th>Theme name</th>"
                '<th class="ri-theme-num">Review count</th>'
                '<th class="ri-theme-num">Percentage share</th>'
                f"</tr></thead><tbody>{rows}</tbody></table></div>",
                unsafe_allow_html=True,
            )
        else:
            caption("No theme data available.")

    section_title("Theme descriptions")
    if not themes:
        caption("No theme descriptions available.")
    for row in themes:
        st.markdown(
            item_card(
                title=f'{row.get("id", "")} · {row.get("name", "")}',
                detail=row.get("description", ""),
                meta_left=f'{row.get("percentage", 0)}% of sample',
            ),
            unsafe_allow_html=True,
        )


def render_pain_points(data: dict[str, Any]) -> None:
    points = data.get("pain_points", [])

    section_title("Pain point signal by category")
    if points:
        chart(
            horizontal_bar_chart(
                [row["category"] for row in points],
                [row["mentions"] for row in points],
                title="Illustrative mention counts",
                color=PALETTE["amber"],
                height=330,
            )
        )
    else:
        caption("No pain point data available.")

    section_title("Detail by category")
    if not points:
        caption("No pain point details available.")
    for row in points:
        st.markdown(
            item_card(
                title=row.get("category", ""),
                detail=row.get("summary", ""),
                meta_left=f'{row.get("mentions", 0):,} mentions',
                badge_text=row.get("severity", "Neutral"),
                badge_tone=_tone_for_severity(row.get("severity", "")),
            ),
            unsafe_allow_html=True,
        )


def render_recommendations(data: dict[str, Any]) -> None:
    recommendations = data.get("recommendations", [])

    st.markdown(
        '<div class="ri-muted">Each item below links an identified problem to its supporting '
        'evidence and a suggested product improvement. Priorities are illustrative.</div>',
        unsafe_allow_html=True,
    )

    if not recommendations:
        caption("No recommendations listed.")
        return

    for index, row in enumerate(recommendations, start=1):
        detail = (
            f'<div class="ri-item-detail"><strong>Identified problem:</strong> '
            f'{row.get("problem", "")}</div>'
            f'<div class="ri-item-detail"><strong>Supporting evidence:</strong> '
            f'{row.get("evidence", "")}</div>'
            f'<div class="ri-item-detail"><strong>Suggested improvement:</strong> '
            f'{row.get("improvement", "")}</div>'
        )
        st.markdown(
            item_card(
                title=f"R{index} · {row.get('problem', '')}",
                detail=detail,
                badge_text=f'Priority: {row.get("priority", "Neutral")}',
                badge_tone=_tone_for_severity(row.get("priority", "")),
            ),
            unsafe_allow_html=True,
        )


def render_fee_analysis(data: dict[str, Any]) -> None:
    fees = data.get("fee_analysis", {})
    classification = fees.get("classification", [])
    pilot_size = fees.get("pilot_sample_size", 0)

    st.markdown(
        '<div class="ri-muted">This section presents a small pilot sample. Fee-related claims are '
        'not asserted as fact and must be verified against official sources before use.</div>',
        unsafe_allow_html=True,
    )

    kpi_row(
        [
            {
                "label": "Pilot sample size",
                "value": f"{pilot_size:,}",
                "delta": "reviews sampled",
                "tone": "neutral",
            },
            {
                "label": "Fee-related mentions",
                "value": f'{sum(row["count"] for row in classification if "fee" in row["category"].lower()):,}',
                "delta": "illustrative",
                "tone": "neutral",
            },
            {
                "label": "Fact-check items",
                "value": str(len(fees.get("fact_check", []))),
                "delta": "pending verification",
                "tone": "neutral",
            },
        ]
    )

    left, right = st.columns(2)
    with left:
        section_title("Fee classification categories")
        if classification:
            chart(
                bar_chart(
                    [row["category"] for row in classification],
                    [row["count"] for row in classification],
                    title="Pilot classification counts",
                    y_title="Reviews",
                    height=340,
                )
            )
        else:
            caption("No classification data available.")
    with right:
        section_title("Classification mix")
        if classification:
            chart(
                donut_chart(
                    [row["category"] for row in classification],
                    [row["count"] for row in classification],
                    title="Pilot mix",
                    colors=[PALETTE["teal"], PALETTE["blue"], PALETTE["amber"]],
                    height=340,
                )
            )
        else:
            caption("No classification data available.")

    section_title("Fact-check status")
    for row in fees.get("fact_check", []):
        st.markdown(
            item_card(
                title=row.get("item", ""),
                detail="Verify against an official source before publishing any finding.",
                badge_text=row.get("status", "Pending verification"),
                badge_tone="medium",
            ),
            unsafe_allow_html=True,
        )

    section_title("Official source links")
    sources = fees.get("sources", [])
    if sources:
        lines = "\n".join(
            f'- <a class="ri-link" href="{row.get("url", "#")}" target="_blank" rel="noopener">'
            f'{row.get("label", "Source")}</a>'
            for row in sources
        )
        st.markdown(
            f'<div class="ri-panel"><div class="ri-muted">{lines}</div></div>',
            unsafe_allow_html=True,
        )
        caption("Placeholder URLs are shown. Replace them with verified official links in report.json.")
    else:
        caption("No source links provided.")
