"""Groww Review Analyzer - Play Store Review Analytics.

Run with:
    streamlit run app.py
"""

from __future__ import annotations

import streamlit as st

from components.ui import load_css, page_header, sidebar_brand
from data.loader import load_report_data
from sections_platform import (
    render_data_quality_section,
    render_fee_explainer_section,
    render_how_it_works_section,
    render_overview_section,
    render_product_insights_section,
    render_weekly_pulse_section,
)

SECTIONS = {
    "Overview": render_overview_section,
    "Weekly pulse": render_weekly_pulse_section,
    "Product insights": render_product_insights_section,
    "Fee explainer": render_fee_explainer_section,
    "Data & quality checks": render_data_quality_section,
    "How it works": render_how_it_works_section,
}

PAGE_TITLES = {
    "Overview": "Overview",
    "Weekly pulse": "Weekly Pulse",
    "Product insights": "Product Insights",
    "Fee explainer": "Fee Explainer",
    "Data & quality checks": "Data & Quality Checks",
    "How it works": "How It Works",
}

PAGE_DESCRIPTIONS = {
    "Overview": (
        "Groww Review Analyzer transforms Play Store reviews into actionable product insights, "
        "with a fact-checked fee explainer and a human approval step before any report is published."
    ),
    "Weekly pulse": "Track changes in customer feedback and ratings over time.",
    "Product insights": "Understand customer needs, pain points and product opportunities.",
    "Fee explainer": (
        "Understand fee-related customer feedback and explore claims verified against "
        "official Groww sources."
    ),
    "Data & quality checks": "Data quality, consistency and validation checks.",
    "How it works": "Understand the end-to-end review intelligence pipeline.",
}


def render_sidebar() -> str:
    with st.sidebar:
        sidebar_brand()
        st.markdown('<div class="sidebar-nav-label">WORKSPACE</div>', unsafe_allow_html=True)
        selection = st.radio(
            "Navigation",
            options=list(SECTIONS),
            label_visibility="collapsed",
        )
        st.markdown(
            '<div class="sidebar-footer">'
            '<div class="sidebar-footer-heading">ABOUT THIS PROJECT</div>'
            '<div>Independent product analytics case study.</div>'
            '<div>Data sourced from Groww Play Store reviews.</div>'
            '<div>Not affiliated with Groww.</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<style>'
            '.sidebar-github-link{display:inline-flex;align-items:center;gap:0.45rem;'
            'margin:0.45rem 0.75rem 0;padding:0.25rem 0.3rem;border-radius:6px;'
            'color:var(--ri-accent);font-size:0.74rem;font-weight:600;'
            'text-decoration:none;transition:color 0.15s ease,background-color 0.15s ease;}'
            '.sidebar-github-link svg{width:14px;height:14px;flex:0 0 14px;'
            'transition:transform 0.15s ease;}'
            '.sidebar-github-link .sidebar-github-external{font-size:0.7rem;opacity:0.75;}'
            '.sidebar-github-link:hover{color:var(--ri-text);background:var(--ri-accent-soft);'
            'text-decoration:underline;}'
            '.sidebar-github-link:hover svg{transform:translateY(-1px);}'
            '.sidebar-github-link:focus-visible{outline:2px solid var(--ri-accent-line);'
            'outline-offset:2px;}'
            '[data-testid="stSidebar"] .sidebar-github-link{color:var(--ri-accent);'
            'text-decoration:none;}'
            '[data-testid="stSidebar"] .sidebar-github-link:hover{color:var(--ri-text);'
            'text-decoration:underline;}'
            '</style>'
            '<a class="sidebar-github-link"'
            ' href="https://github.com/ManlivK/groww-review-analyzer"'
            ' target="_blank" rel="noopener noreferrer"'
            ' aria-label="View on GitHub (opens in a new tab)"'
            ' title="View on GitHub (opens in a new tab)">'
            '<svg viewBox="0 0 16 16" fill="currentColor" aria-hidden="true">'
            '<path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 '
            '0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-'
            '.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52'
            '.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36'
            '-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 '
            '1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 '
            '3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15'
            '.46.55.38A8.01 8.01 0 0016 8c0-4.42-3.58-8-8-8z"></path>'
            '</svg>'
            '<span>View on GitHub</span>'
            '<span class="sidebar-github-external" aria-hidden="true">↗</span>'
            '</a>',
            unsafe_allow_html=True,
        )
    return selection


def main() -> None:
    st.set_page_config(
        page_title="Groww Review Analyzer",
        page_icon="RI",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    load_css()

    data = load_report_data()
    selection = render_sidebar()
    page_header(
        data.get("meta", {}),
        PAGE_TITLES.get(selection, selection),
        description=PAGE_DESCRIPTIONS.get(selection, ""),
    )
    SECTIONS[selection](data)


if __name__ == "__main__":
    main()
