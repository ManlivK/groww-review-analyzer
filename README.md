# Groww Review Pulse — AI-Powered Play Store Review Analyzer

An AI-powered workflow that transforms Google Play Store reviews into structured product insights, weekly sentiment reports, and actionable recommendations.

## Project Overview

Product teams receive thousands of app reviews, making it difficult to identify recurring customer complaints, understand sentiment changes, and prioritize product improvements.

**Groww Review Pulse** automates this process using n8n, Google Gemini, and MCP integrations.

The workflow processes Groww Play Store reviews, identifies customer feedback themes, analyses weekly trends, generates a fee explainer using official sources, and prepares a product report for review.

## Key Features

- **Review cleaning:** Removes blank reviews, short reviews, and duplicates.
- **Balanced sampling:** Limits the analysis dataset to a maximum of 200 reviews per week.
- **AI-powered theme discovery:** Identifies up to five distinct customer feedback themes.
- **Batch classification:** Classifies individual reviews into predefined themes using Google Gemini.
- **Sentiment and trend analysis:** Compares review volume, low ratings, high ratings, and average ratings across reporting periods.
- **Fee-related analysis:** Identifies fee-related reviews and classifies a pilot sample.
- **Official-source validation:** Generates a fee explainer using Groww's official pricing and help pages, followed by an AI fact-checking step.
- **Report generation:** Prepares a weekly product pulse with customer pain points and recommendations.
- **MCP integration:** Connects the workflow to Google Docs and Gmail for document verification, report append, and email draft creation.

## Architecture

```text
Google Play Store Reviews (CSV)
              |
              v
       n8n Main Pipeline
              |
              v
      Review Cleaning
              |
              v
      Theme Discovery
              |
              v
     Batch Classification
              |
              v
       Weekly Analysis
              |
              v
       Fee Analysis
              |
              v
   Official Source Validation
              |
              v
      Report Generation
              |
              v
        Human Review
              |
              v
        MCP Server
          /       \
         v         v
    Google Docs   Gmail Draft
```

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Review data preparation and preprocessing |
| n8n | Workflow orchestration and automation |
| Google Gemini | Theme discovery, classification, and report generation |
| MCP | Integration with external tools |
| Google Docs | Weekly report storage |
| Gmail | Email draft creation |
| GitHub | Source control and project showcase |
| Streamlit | Planned interactive dashboard |

## Workflow Components

### 1. Main Pipeline

File: `groww-review-pipeline-public.json`

The main n8n workflow handles:

1. CSV upload and extraction.
2. Review cleaning and duplicate removal.
3. Weekly review limits.
4. AI-powered theme discovery.
5. Batch-based review classification.
6. Weekly product pulse generation.
7. Fee-related review analysis.
8. Official-source fee explanation and fact-checking.
9. Final report and email content preparation.

### 2. MCP Server

File: `groww-review-mcp-server-public.json`

The MCP Server exposes three tools:

| Tool | Function |
|---|---|
| `read_doc` | Reads the existing weekly report to verify content and check duplicates. |
| `append_to_doc` | Appends an approved weekly report to Google Docs. |
| `create_email_draft` | Creates an email draft containing the weekly report. |

Human approval is part of the reporting process. The email integration creates a draft rather than automatically sending the report.

## Analysis Scope

The current analysis run includes:

| Metric | Result |
|---|---:|
| Cleaned reviews available | 6,042 |
| Reviews selected for analysis | 2,404 |
| Unique classified review IDs | 2,404 |
| Duplicate theme records | 0 |
| Discovered themes | 5 |

### Discovered Customer Themes

| Theme ID | Theme |
|---|---|
| T1 | Technical Performance and Stability |
| T2 | Customer Support and Operational Delays |
| T3 | Pricing and Fee Structure |
| T4 | UI/UX Design and Feature Gaps |
| T5 | Ease of Use and Accessibility |

**Important:** Fee classification was performed on a pilot sample of 25 out of 227 fee-related reviews. Its findings are provisional and should not be interpreted as conclusions from the entire fee-related dataset.

## Official Sources

The fee explainer uses the following official Groww resources:

- [Groww Pricing](https://groww.in/pricing)
- [Groww Help Centre — Additional Charges](https://groww.in/help/payments-%26-withdrawals/payments-charges/apart-from-brokerage--what-fees-am-i-charged--93)

## Setup and Configuration

The repository contains sanitized n8n workflow exports for reference and reuse.

To run the workflows in your own n8n instance:

1. Import the main pipeline JSON.
2. Configure your own Google Gemini credentials.
3. Configure the required n8n Data Table.
4. Import the MCP Server workflow separately.
5. Configure your own Google Docs and Gmail credentials.
6. Configure the MCP endpoint and authentication.
7. Replace document references, recipient details, and other environment-specific settings.
8. Upload your own review CSV and test the workflow.

**Note:** The exported workflows are templates, not turnkey deployments. Credentials, Data Tables, document references, and environment-specific configuration must be supplied by the user.

## Project Status

- [x] Review cleaning and preparation
- [x] AI theme discovery
- [x] Batch-based theme classification
- [x] Weekly product pulse generation
- [x] Fee explainer and fact-check workflow
- [x] Google Docs and Gmail MCP integration
- [x] Sanitized n8n workflow exports
- [ ] Streamlit dashboard
- [ ] Cloud deployment

## Future Improvements

- Interactive Streamlit dashboard for product insights.
- Visualize weekly rating and review-volume trends.
- Explore customer feedback by theme.
- Track recurring product pain points.
- Enable easier report exploration and sharing.

## Disclaimer

This is an independent portfolio project built for product analytics and workflow automation demonstration. It is not affiliated with or endorsed by Groww.

AI-generated classifications and recommendations may require human review. Fee information should always be checked against the latest official Groww sources.

---

**Built with Python, n8n, Google Gemini, and MCP.**

## Workflow Screenshots

### 1. Complete n8n Workflow
![Workflow Overview](screenshots/workflow-overview.png.png)

### 2. Review Processing and AI Classification
![Review Processing](screenshots/review-processing-classification.png.png)

### 3. Reporting and Fact-Checking
![Reporting Workflow](screenshots/reporting-fact-checking-and-mcp.png.png)

### 4. MCP Server Architecture
![MCP Server](screenshots/mcp-server-architecture.png.png)

# Groww Review Analyzer
### AI-Powered Customer Feedback & Product Intelligence

An end-to-end AI-powered workflow that transforms Google Play Store reviews into actionable product insights, customer feedback themes, weekly trends and recommendations.

< p align="center">
  <a href="https://groww-review-analyzer-yvf7rdbgrwqv5dx8xkccjs.streamlit.app/">
    <strong>🚀 View Live Dashboard</strong>
  </a>
</p>

---

## 📌 Project Overview

App reviews contain valuable customer feedback, but manually analysing thousands of reviews makes it difficult to identify recurring problems, understand customer sentiment and prioritise product improvements.

**Groww Review Analyzer** automates this process by combining Python, AI, n8n and MCP integrations.

The solution collects and prepares Play Store reviews, identifies customer feedback themes, analyses weekly trends, generates fee-related explanations using official sources, and presents the results through a Streamlit dashboard.

## ✨ Key Features

- **Review Processing:** Cleans reviews by removing duplicates, blank entries and short reviews.
- **AI-Powered Theme Discovery:** Identifies recurring customer feedback themes.
- **Review Classification:** Uses AI to classify individual reviews into discovered themes.
- **Weekly Pulse Analysis:** Tracks review volume, average ratings and rating distribution.
- **Product Insights:** Highlights customer pain points and positive feedback.
- **Fee Explainer:** Analyses fee-related reviews and generates explanations using official Groww sources.
- **Fact-Checking:** Validates generated fee-related claims against retrieved source information.
- **MCP Integration:** Connects the workflow with Google Docs and Gmail.
- **Human-in-the-Loop:** Includes a review and approval step before report publication.
- **Interactive Dashboard:** Visualises product insights and analysis results using Streamlit and Plotly.

## 📊 Analysis Highlights

The current analysis covers the reporting period **19 October 2026 – 9 November 2026**.

| Metric | Result |
|---|---:|
| Cleaned reviews | 6,042 |
| Reviews analysed | 2,404 |
| Customer feedback themes | 5 |
| Fee-related reviews identified | 227 |
| Reviews in fee classification pilot | 25 |

### Customer Feedback Themes

| Theme | Reviews | Share |
|---|---:|---:|
| Ease of Use and Accessibility | 1,083 | 45.0% |
| UI/UX Design and Feature Gaps | 404 | 16.8% |
| Technical Performance and Stability | 351 | 14.6% |
| Customer Support and Operational Delays | 335 | 13.9% |
| Pricing and Fee Structure | 231 | 9.6% |

*The fee classification is a pilot involving 25 of the 227 identified fee-related reviews. Its findings are preliminary and do not represent the entire fee-related dataset.*

## 🖥️ Dashboard Preview

Explore the deployed dashboard:

**[Groww Review Analyzer – Live Dashboard](https://groww-review-analyzer-yvf7rdbgrwqv5dx8xkccjs.streamlit.app/)**

The dashboard contains six sections:

| Section | Description |
|---|---|
| Overview | Key metrics and executive summary |
| Weekly Pulse | Weekly review and rating trends |
| Product Insights | Customer feedback themes and pain points |
| Fee Explainer | Fee-related analysis and explanations |
| Data & Quality Checks | Data validation and analysis limitations |
| How It Works | Project workflow and architecture |

## ⚙️ System Architecture

```text
Google Play Store Reviews
          |
          v
Python - Review Cleaning & Preparation
          |
          v
       n8n Workflow
          |
          v
   AI Theme Discovery
          |
          v
  Batch Review Classification
          |
          v
  Weekly Pulse & Fee Analysis
          |
          v
 Official Source Retrieval
          |
          v
   Fee Fact-Checking
          |
          v
   Report Generation
          |
          v
 Human Review & Approval
          |
          v
      MCP Server
       /      \
      v        v
 Google Docs  Gmail Draft
          |
          v
  Structured Report Output
          |
          v
  Streamlit Dashboard
```

## 🛠️ Technology Stack

| Technology | Usage |
|---|---|
| Python | Review processing and data preparation |
| Pandas | Data manipulation and analysis |
| n8n | Workflow automation and orchestration |
| Google Gemini | AI-based theme discovery, classification and summarisation |
| MCP | Integration with Google Docs and Gmail |
| Streamlit | Dashboard development |
| Plotly | Interactive data visualisation |
| Git & GitHub | Version control and project hosting |

## 🔄 Workflow Components

### 1. Main n8n Pipeline

File: `groww-review-pipeline-public.json`

The main workflow automates review processing, AI-based theme discovery, batch classification, weekly trend analysis, fee-related analysis, fact-checking and report generation.

### 2. MCP Server

File: `groww-review-mcp-server-public.json`

The MCP server provides tools to:

- Read existing Google Docs reports.
- Append approved reports to Google Docs.
- Create Gmail drafts containing report updates.

The Gmail integration creates drafts rather than automatically sending emails.

## 📂 Repository Structure

```text
groww-review-analyzer/
│
├── app.py
├── sections.py
├── sections_platform.py
├── requirements.txt
│
├── components/
│   ├── charts.py
│   └── ui.py
│
├── data/
│   ├── loader.py
│   ├── report.json
│   ├── sample_data.py
│   └── validation.py
│
├── styles/
│   └── custom.css
│
├── .streamlit/
│   └── config.toml
│
├── screenshots/
│   ├── workflow-overview.png.png
│   ├── review-processing-classification.png.png
│   ├── reporting-fact-checking-and-mcp.png.png
│   └── mcp-server-architecture.png.png
│
├── groww-review-pipeline-public.json
├── groww-review-mcp-server-public.json
├── .gitignore
└── README.md
```

## 🚀 Run Locally

Clone the repository:

```bash
git clone https://github.com/ManlivK/groww-review-analyzer.git
```

Navigate to the project directory:

```bash
cd groww-review-analyzer
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the Streamlit application:

```bash
streamlit run app.py
```

## 🔍 Project Learnings

Through this project, I explored and implemented:

- AI-powered analysis of unstructured customer feedback.
- Batch processing to manage large-scale review classification.
- Workflow automation using n8n.
- Human-in-the-loop approval for AI-generated reports.
- MCP-based integration with external applications.
- Data validation and quality checks.
- Building a data-driven product analytics dashboard.

## ⚠️ Limitations

- Analysis is based on a selected and balanced review dataset, not every review available on the Play Store.
- Fee classification covers a 25-review pilot from 227 fee-related reviews.
- AI-generated classifications and recommendations may require human review.
- Fee information should always be checked against the latest official Groww sources.

## 📚 Official Sources

- [Groww Pricing](https://groww.in/pricing)
- [Groww Help Centre – Additional Charges](https://groww.in/help/payments-%26-withdrawals/payments-charges/apart-from-brokerage--what-fees-am-i-charged--93)

## 👩‍💻 Author

Built as an independent portfolio project to explore the intersection of **AI, workflow automation, product analytics and data visualisation**.

**GitHub:** [ManlivK](https://github.com/ManlivK)

---

*Disclaimer: This is an independent portfolio project and is not affiliated with or endorsed by Groww.*
