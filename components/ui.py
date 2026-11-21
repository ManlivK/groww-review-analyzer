"""Reusable Streamlit UI primitives for the dashboard."""

from __future__ import annotations

from html import escape
from pathlib import Path
from typing import Any, Iterable

import streamlit as st

_CSS_PATH = Path(__file__).resolve().parent.parent / "styles" / "custom.css"

_DELTA_ICONS = {"positive": "\u25b2", "negative": "\u25bc", "neutral": "\u2022"}

_PAGE_HEADER_TEMPLATE = (
    '<div class="ri-page-header">'
    '<div class="ri-page-title">{title}</div>'
    '<div class="ri-page-description">{description}</div>'
    '<div class="ri-page-accent"></div>'
    '</div>'
)

_RI_LOGO_SVG = """<svg class="ri-logo-svg" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="riLogoTitle">
<title id="riLogoTitle">RI Review Intelligence</title>
<defs>
<linearGradient id="riLogoGradient" x1="0" y1="0" x2="1" y2="1">
<stop offset="0" stop-color="#268C78"/>
<stop offset="1" stop-color="#17584C"/>
</linearGradient>
</defs>
<rect x="0.75" y="0.75" width="46.5" height="46.5" rx="13.5" fill="url(#riLogoGradient)"/>
<text x="7" y="31.5" fill="#FFFDF8" font-family="Arial, Helvetica, sans-serif" font-size="18" font-weight="700" letter-spacing="-1">RI</text>
<rect x="28.6" y="25.8" width="3.6" height="8" rx="1.5" fill="#A8DCCF"/>
<rect x="33.7" y="21.5" width="3.6" height="12.3" rx="1.5" fill="#CDEFE6"/>
<rect x="38.8" y="17" width="3.6" height="16.8" rx="1.5" fill="#FFFDF8"/>
<path d="M30.4 22.6L35.5 18.2L40.6 13.8" fill="none" stroke="#FFFDF8" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
<circle cx="40.6" cy="13.8" r="1.8" fill="#FFFDF8"/>
</svg>"""

_BRAND_TEMPLATE = (
    '<div class="sidebar-brand">'
    '<div class="sidebar-brand-mark">{logo}</div>'
    '<div class="sidebar-brand-text">'
    '<div class="sidebar-brand-name">{name}</div>'
    '</div>'
    '</div>'
)


def load_css() -> None:
    """Inject the project stylesheet into the Streamlit app."""
    st.markdown(f"<style>{_CSS_PATH.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


def sidebar_brand(name: str = "Groww Review Analyzer") -> None:
    """Render the shared RI logo and product name in the sidebar."""
    st.markdown(
        _BRAND_TEMPLATE.format(logo=_RI_LOGO_SVG, name=escape(name)),
        unsafe_allow_html=True,
    )


def badge(text: str, tone: str = "neutral") -> str:
    """Return HTML for a small status badge."""
    return f'<span class="ri-badge ri-badge-{tone}">{text}</span>'


def page_header(meta: dict[str, Any], title: str, description: str = "") -> None:
    """Render the shared page header and sample-data notice."""
    st.markdown(
        _PAGE_HEADER_TEMPLATE.format(
            title=escape(title),
            description=escape(description),
        ),
        unsafe_allow_html=True,
    )
    if meta.get("is_sample", False):
        sample_label = escape(str(meta.get("sample_label", "Illustrative sample data")))
        sample_note = escape(str(meta.get("sample_note", "")))
        st.markdown(
            f'<span class="ri-badge ri-badge-sample">{sample_label}</span>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="ri-sample-note">{sample_note}</div>',
            unsafe_allow_html=True,
        )


def section_title(text: str) -> None:
    st.markdown(f'<div class="ri-section-title">{text}</div>', unsafe_allow_html=True)


def kpi_card(
    label: str,
    value: str,
    delta: str = "",
    tone: str = "neutral",
    *,
    scope: str = "",
) -> str:
    """Return HTML for a single KPI card."""
    icon = _DELTA_ICONS.get(tone, "\u2022")
    delta_html = (
        f'<div class="ri-kpi-delta ri-kpi-delta-{tone}">{icon} {delta}</div>' if delta else ""
    )
    scope_class = f" ri-kpi-card-{scope}" if scope else ""
    return (
        f'<div class="ri-kpi-card{scope_class}">'
        f'<div class="ri-kpi-label">{label}</div>'
        f'<div class="ri-kpi-value">{value}</div>'
        f'{delta_html}'
        '</div>'
    )


def kpi_row(kpis: Iterable[dict[str, Any]], *, scope: str = "") -> None:
    """Render a row of KPI cards inside equal-width columns."""
    kpis = list(kpis)
    if not kpis:
        return
    columns = st.columns(len(kpis))
    for column, item in zip(columns, kpis):
        with column:
            st.markdown(
                kpi_card(
                    label=item.get("label", ""),
                    value=str(item.get("value", "")),
                    delta=item.get("delta", ""),
                    tone=item.get("tone", "neutral"),
                    scope=scope,
                ),
                unsafe_allow_html=True,
            )


def item_card(
    title: str,
    detail: str = "",
    *,
    meta_left: str = "",
    badge_text: str = "",
    badge_tone: str = "neutral",
) -> str:
    """Return HTML for a compact information card."""
    detail_html = f'<div class="ri-item-detail">{detail}</div>' if detail else ""
    badge_html = badge(badge_text, badge_tone) if badge_text else ""
    left_html = f'<span class="ri-metric-inline">{meta_left}</span>' if meta_left else "<span></span>"
    return (
        '<div class="ri-item">'
        f'<div class="ri-item-title">{title}</div>'
        f'{detail_html}'
        '<div class="ri-item-meta">'
        f'{left_html}{badge_html}'
        '</div>'
        '</div>'
    )


def panel(html: str) -> None:
    """Wrap arbitrary HTML in a bordered panel."""
    st.markdown(f'<div class="ri-panel">{html}</div>', unsafe_allow_html=True)


def caption(text: str) -> None:
    st.markdown(f'<div class="ri-muted">{text}</div>', unsafe_allow_html=True)


def chart(figure: Any) -> None:
    """Render a Plotly figure responsively across Streamlit versions."""
    try:
        st.plotly_chart(figure, width="stretch")
    except TypeError:
        st.plotly_chart(figure, use_container_width=True)
