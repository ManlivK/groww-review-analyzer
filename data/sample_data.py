"""Illustrative sample data for the Groww Review Analyzer dashboard.

All values in this module are placeholders used only to demonstrate the UI.
They are not findings about any real product or company. To use real data,
place a JSON report at ``data/report.json`` with the same structure, or pass
an explicit path to :func:`data.loader.load_report_data`.
"""

SAMPLE_DATA = {
    "meta": {
        "title": "Groww Review Analyzer",
        "subtitle": "Play Store Review Analytics",
        "context": "Independent product analytics case study",
        "is_sample": True,
        "sample_label": "Illustrative sample data",
        "sample_note": (
            "All figures, themes and recommendations shown here are placeholder "
            "values for interface demonstration only. They are not real business findings."
        ),
    },
    "overview": {
        "kpis": [
            {
                "label": "Total reviews analysed",
                "value": "12,840",
                "delta": "+8.2% vs prior period",
                "tone": "positive",
            },
            {
                "label": "Average rating",
                "value": "4.1 / 5",
                "delta": "+0.2 vs prior period",
                "tone": "positive",
            },
            {
                "label": "Discovered themes",
                "value": "5",
                "delta": "T1 – T5",
                "tone": "neutral",
            },
            {
                "label": "Fee analysis pilot",
                "value": "240",
                "delta": "reviews sampled",
                "tone": "neutral",
            },
        ],
        "weekly_rating_trend": [
            {"week": "W1", "rating": 3.8},
            {"week": "W2", "rating": 3.9},
            {"week": "W3", "rating": 4.0},
            {"week": "W4", "rating": 3.9},
            {"week": "W5", "rating": 4.1},
            {"week": "W6", "rating": 4.2},
            {"week": "W7", "rating": 4.1},
            {"week": "W8", "rating": 4.3},
        ],
        "feedback_distribution": [
            {"label": "Positive", "value": 58, "color": "#26B99A"},
            {"label": "Neutral", "value": 24, "color": "#4C8DFF"},
            {"label": "Negative", "value": 18, "color": "#EF6F6C"},
        ],
        "opportunities": [
            {
                "title": "Improve crash-free sessions",
                "detail": "Stability is the largest negative theme in the sample.",
                "impact": "High",
            },
            {
                "title": "Shorten support response time",
                "detail": "Support mentions repeat across the sampled period.",
                "impact": "High",
            },
            {
                "title": "Clarify fee communication",
                "detail": "Fee-related questions appear in the pilot sample.",
                "impact": "Medium",
            },
        ],
    },
    "trends": {
        "weekly_volume": [
            {"week": "W1", "reviews": 1180},
            {"week": "W2", "reviews": 1340},
            {"week": "W3", "reviews": 1260},
            {"week": "W4", "reviews": 1490},
            {"week": "W5", "reviews": 1620},
            {"week": "W6", "reviews": 1510},
            {"week": "W7", "reviews": 1730},
            {"week": "W8", "reviews": 1810},
        ],
        "rating_trend": [
            {"week": "W1", "rating": 3.8},
            {"week": "W2", "rating": 3.9},
            {"week": "W3", "rating": 4.0},
            {"week": "W4", "rating": 3.9},
            {"week": "W5", "rating": 4.1},
            {"week": "W6", "rating": 4.2},
            {"week": "W7", "rating": 4.1},
            {"week": "W8", "rating": 4.3},
        ],
        "rating_split": [
            {"week": "W1", "low": 290, "high": 690},
            {"week": "W2", "low": 310, "high": 780},
            {"week": "W3", "low": 270, "high": 760},
            {"week": "W4", "low": 340, "high": 830},
            {"week": "W5", "low": 300, "high": 910},
            {"week": "W6", "low": 260, "high": 940},
            {"week": "W7", "low": 280, "high": 1020},
            {"week": "W8", "low": 240, "high": 1090},
        ],
    },
    "themes": [
        {
            "id": "T1",
            "name": "Technical stability",
            "percentage": 31,
            "description": "Crashes, login failures and slow loading mentioned by reviewers.",
        },
        {
            "id": "T2",
            "name": "Customer support",
            "percentage": 24,
            "description": "Response time and resolution quality of support interactions.",
        },
        {
            "id": "T3",
            "name": "Pricing and fees",
            "percentage": 19,
            "description": "Questions and concerns about charges and fee transparency.",
        },
        {
            "id": "T4",
            "name": "UI/UX issues",
            "percentage": 14,
            "description": "Navigation clarity, layout and usability feedback.",
        },
        {
            "id": "T5",
            "name": "Positive feedback",
            "percentage": 12,
            "description": "Praise for ease of use and overall product experience.",
        },
    ],
    "pain_points": [
        {
            "category": "Technical stability",
            "mentions": 412,
            "severity": "High",
            "summary": "Intermittent crashes and slow screens dominate negative reviews in the sample.",
        },
        {
            "category": "Customer support",
            "mentions": 318,
            "severity": "High",
            "summary": "Reviewers describe delayed responses and repeated clarification requests.",
        },
        {
            "category": "Pricing and fees",
            "mentions": 251,
            "severity": "Medium",
            "summary": "Pilot sample contains questions about when and how fees are applied.",
        },
        {
            "category": "UI/UX issues",
            "mentions": 184,
            "severity": "Medium",
            "summary": "Some flows are reported as hard to locate or confusing on small screens.",
        },
        {
            "category": "Positive feedback",
            "mentions": 156,
            "severity": "Low",
            "summary": "Reviewers highlight simplicity and fast onboarding as strengths.",
        },
    ],
    "recommendations": [
        {
            "problem": "Recurring stability complaints",
            "evidence": "T1 is the largest negative theme in the illustrative dataset.",
            "improvement": "Prioritise crash monitoring and release-quality regression checks.",
            "priority": "High",
        },
        {
            "problem": "Slow support resolution",
            "evidence": "Support-related mentions remain consistent across all sample weeks.",
            "improvement": "Add templated responses and a escalation tracker for repeat issues.",
            "priority": "High",
        },
        {
            "problem": "Unclear fee communication",
            "evidence": "Fee questions appear in the pilot sample of 240 reviews.",
            "improvement": "Surface fee details earlier in the flow and link to official documentation.",
            "priority": "Medium",
        },
        {
            "problem": "Navigation friction",
            "evidence": "UI/UX theme is present across the sampled review period.",
            "improvement": "Run usability tests on the top affected screens before redesign.",
            "priority": "Medium",
        },
    ],
    "fee_analysis": {
        "pilot_sample_size": 240,
        "classification": [
            {"category": "Fee-related question", "count": 78},
            {"category": "General pricing mention", "count": 54},
            {"category": "Not fee-related", "count": 108},
        ],
        "fact_check": [
            {
                "item": "Fee amount and applicability",
                "status": "Pending verification",
            },
            {
                "item": "Effective date of any fee change",
                "status": "Pending verification",
            },
            {
                "item": "Exemptions and eligibility rules",
                "status": "Pending verification",
            },
        ],
        "sources": [
            {
                "label": "Official fee schedule (add link)",
                "url": "https://example.com/official-fee-schedule",
            },
            {
                "label": "Official help centre article (add link)",
                "url": "https://example.com/official-help-centre",
            },
            {
                "label": "Terms and conditions (add link)",
                "url": "https://example.com/official-terms",
            },
        ],
    },
}
