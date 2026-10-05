# Company Financial Health Dashboard

A beginner-friendly Flask project for CMU 15-113 Project 2.

The app lets a user search for a public company ticker. The current starter version uses mock Apple data so the frontend dashboard works before SEC EDGAR integration is added.

## Architecture

Browser -> Flask backend -> SEC API later -> Python calculations -> Flask JSON response -> JavaScript dashboard

## Project Structure

```text
.
├── app.py
├── sec_client.py
├── financial_metrics.py
├── requirements.txt
├── README.md
├── prompt_log.md
├── templates/
│   └── index.html
└── static/
    ├── styles.css
    └── app.js
```

## Setup

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the app:

```bash
python app.py
```

Open the app in your browser:

```text
http://127.0.0.1:5001
```

## Current Starter Behavior

- Homepage route: `/`
- API route: `/api/company/<ticker>`
- Mock data is currently available for `AAPL`
- The dashboard shows overview cards and a Chart.js revenue/net income chart

## Next Steps

- Add real SEC EDGAR Company Facts requests in `sec_client.py`
- Add more metric calculations in `financial_metrics.py`
- Improve error handling for missing or incomplete SEC data
