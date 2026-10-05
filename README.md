# Company Financial Health Dashboard

A Flask web app for CMU 15-113 Project 2 that lets users search for a public company ticker, fetch real SEC EDGAR Company Facts data, calculate financial metrics, visualize annual trends, and generate a plain-English AI explanation of the calculated results.

This project is for educational financial analysis only and is not investment advice.

## Features

- Search by ticker symbol, such as `AAPL`, `MSFT`, `NKE`, or `KO`
- Fetch real company data from the SEC EDGAR Company Facts API
- Convert ticker symbols into SEC CIK identifiers
- Extract annual 10-K financial facts from raw XBRL-style SEC data
- Calculate revenue growth, profit margin, operating margin, liabilities/assets, and return on assets
- Display interactive Chart.js visualizations for performance, margins, and balance sheet trends
- Generate programmatic key observations from the latest fiscal year versus the prior fiscal year
- Optionally generate an OpenAI-powered explanation using only the app's calculated metrics and observations
- Handle invalid tickers, missing SEC concepts, and missing OpenAI configuration with readable errors

## Architecture

```text
Browser
  -> Flask backend
  -> SEC ticker lookup
  -> SEC Company Facts API
  -> Python metric extraction and calculations
  -> Flask JSON response
  -> JavaScript dashboard and Chart.js visualizations
  -> optional OpenAI explanation
```

The frontend does not call the SEC or OpenAI APIs directly. Flask handles those requests so API keys stay server-side and SEC CORS issues are avoided.

## Project Structure

```text
.
├── app.py                 # Flask routes
├── sec_client.py          # SEC ticker lookup and Company Facts requests
├── financial_metrics.py   # XBRL concept extraction and financial calculations
├── ai_explainer.py        # OpenAI explanation helper
├── requirements.txt       # Python dependencies
├── README.md
├── prompt_log.md
├── templates/
│   └── index.html
└── static/
    ├── styles.css
    └── app.js
```

## Local Setup

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a local `.env` file:

```bash
touch .env
```

Add your OpenAI API key:

```text
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-5-mini
```

`OPENAI_MODEL` is optional because the app defaults to `gpt-5-mini`.

Never commit `.env` or any API key. This repository's `.gitignore` excludes `.env`.

Run the app:

```bash
python app.py
```

Open:

```text
http://127.0.0.1:5001
```

## API Routes

### `GET /api/company/<ticker>`

Returns calculated dashboard data for a ticker.

Example:

```text
http://127.0.0.1:5001/api/company/AAPL
```

### `GET /api/explain/<ticker>`

Returns an AI-generated explanation of the already-calculated dashboard data.

Example:

```text
http://127.0.0.1:5001/api/explain/AAPL
```

If `OPENAI_API_KEY` is missing, this route returns a readable JSON error instead of crashing.

## Deployment

This app can be deployed as a Python web service on Render.

Render settings:

```text
Build command: pip install -r requirements.txt
Start command: gunicorn app:app
```

Environment variables:

```text
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-5-mini
```

Do not upload `.env` to GitHub or Render. Add environment variables through Render's dashboard.

## How To Explain The Code

The core data flow is:

```text
Ticker -> SEC ticker lookup -> CIK -> Company Facts JSON -> XBRL concept extraction -> annual 10-K filtering -> financial calculations -> JSON response -> dashboard charts -> optional AI explanation
```

Important files:

- `app.py`: Defines the Flask routes.
- `sec_client.py`: Converts tickers into SEC CIKs and fetches raw SEC data.
- `financial_metrics.py`: Extracts annual financial data and calculates ratios and observations.
- `static/app.js`: Fetches backend JSON and renders tables, charts, tabs, observations, and AI explanation text.
- `ai_explainer.py`: Sends only structured calculated metrics to OpenAI for plain-English explanation.

The AI feature does not fetch company data or invent numbers. It only explains the structured metrics already calculated by the Python backend.
