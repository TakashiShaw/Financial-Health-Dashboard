# Prompt Log

This file documents the major AI prompts used while building the Company Financial Health Dashboard for CMU 15-113 Project 2. I used ChatGPT to plan the project and then used Codex in VS Code to implement focused changes. Smaller debugging questions and minor polish prompts are not included here.

## 1. Initial Flask Scaffold

Purpose: create the starting project structure with Flask, HTML, CSS, JavaScript, Chart.js, and mock data.

Prompt:

```text
I am building CMU 15-113 Project 2: a Company Financial Health Dashboard.

Please scaffold a clean, beginner-readable Flask + HTML/CSS/JavaScript project in this folder.

Goal:
Build an app where a user can search for a public company ticker like AAPL, MSFT, NKE, or KO. The Flask backend will later retrieve SEC EDGAR Company Facts data, calculate financial metrics, and send JSON to the frontend. The frontend will show overview metrics and charts.

For now, create the project structure and a working starter version.

Please create these files:

- app.py
- sec_client.py
- financial_metrics.py
- requirements.txt
- README.md
- prompt_log.md
- .gitignore
- templates/index.html
- static/styles.css
- static/app.js

Starter behavior:
- Flask should serve the homepage at `/`.
- Flask should have an API route `/api/company/<ticker>`.
- For now, the API route can return mock sample data for AAPL so the frontend works before the real SEC integration is added.
- The frontend should have a search input, a button, overview metric cards, and at least one Chart.js chart using the mock API response.
- Use simple, readable code that I can explain in class.
- Add comments only where helpful.
- Do not add the AI explanation layer yet.
- Do not add company comparison yet.
- Keep the app focused on the MVP.

Use this intended architecture:

Browser → Flask backend → SEC API later → Python calculations → Flask JSON response → JavaScript dashboard

After scaffolding, tell me exactly how to install dependencies and run the app locally.
```

Result: Codex created the initial Flask app, project files, mock AAPL API response, frontend search UI, metric cards, and a Chart.js chart.

## 2. Finance Dashboard UI Redesign

Purpose: move away from a generic AI-generated card layout and make the interface feel more like a clean financial analysis tool.

Prompt:

```text
I want to redesign the UI using StockAnalysis.com financial pages as inspiration, especially this kind of layout:
https://stockanalysis.com/stocks/aapl/financials/

Do not copy the site exactly, its branding, or its text. Use it only as layout inspiration.

Please redesign the frontend so the app feels like a clean financial analysis tool instead of a generic AI dashboard.

Keep the backend unchanged.

Update only:
- templates/index.html
- static/styles.css
- static/app.js if needed for class names

Design direction:
- Compact page header with title and ticker search.
- Company header section with company name, ticker, CIK, and latest fiscal year.
- Add a simple tab-like row or section labels such as Overview, Performance, Margins, Balance Sheet, even if only Overview works right now.
- Replace the large metric boxes with a tighter financial summary table or stat row.
- Make the chart section feel integrated with the data, not like a separate big card.
- Use thin divider lines, table-like alignment, and restrained spacing.
- Prefer a practical finance website look over a SaaS landing page look.
- Keep it readable and not too advanced for my class project.
- Mobile layout should still work.
- Do not add new backend features.
- Do not add AI yet.
- Do not add company comparison yet.

After editing, summarize what changed and list the modified files.
```

Result: The UI became more compact and finance-oriented, with a header, company information, tab labels, tables, and integrated charts.

## 3. SEC EDGAR Data Integration

Purpose: replace mock data with real company financial data from the SEC.

Prompt:

```text
The mock dashboard is working and the UI is acceptable for now. Next, replace the mock data with real SEC EDGAR data.

Please implement this in small, readable steps.

Requirements:

1. In sec_client.py:
   - Fetch SEC's company tickers JSON.
   - Match a user-entered ticker like AAPL, MSFT, NKE, or KO.
   - Convert the company's CIK to the 10-digit format required by SEC URLs.
   - Fetch Company Facts JSON from:
     https://data.sec.gov/api/xbrl/companyfacts/CIK##########.json
   - Use a clear User-Agent header.
   - Add helpful error handling for invalid tickers, SEC request failures, and missing data.

2. In financial_metrics.py:
   - Extract annual 10-K facts from the SEC Company Facts JSON.
   - Start with these concepts:
     - Revenue
     - Net income
     - Operating income
     - Total assets
     - Total liabilities
     - Cash
   - Use fallback concept names when needed because companies report similar data with different XBRL tags.
   - Prefer USD units.
   - Prefer annual 10-K data, not quarterly 10-Q data.
   - Calculate:
     - year-over-year revenue growth
     - net profit margin
     - operating margin
     - liabilities as a percentage of assets

3. In app.py:
   - Update /api/company/<ticker> to return real SEC data.
   - Keep the response shape close to the mock data so the frontend keeps working.
   - Return clean JSON error messages when something goes wrong.

4. Do not add the AI explanation layer yet.
5. Do not add company comparison yet.
6. Keep the code beginner-readable because I need to explain it in class.

After editing, explain:
- what each file does
- how ticker → CIK → SEC request → extracted metrics works
- how to test AAPL locally
```

Result: The app began using real SEC ticker lookup and Company Facts data. The backend calculated financial metrics from annual 10-K data and returned clean JSON to the frontend.

## 4. Add Real Dashboard Sections

Purpose: make the Overview, Performance, Margins, and Balance Sheet tabs actually display useful data instead of being mostly placeholder navigation.

Prompt:

```text
The SEC EDGAR integration is working. Now improve the dashboard by making the existing sections more useful without changing the backend architecture.

Please add frontend sections for:
- Overview
- Performance
- Margins
- Balance Sheet

Use the existing API response from /api/company/<ticker>. Do not add AI yet.

Requirements:
1. Overview:
   - Keep the current summary table and revenue/net income chart.

2. Performance:
   - Show annual revenue growth over time.
   - Show revenue and net income trends clearly.

3. Margins:
   - Show net profit margin and operating margin over time.
   - Display percentages cleanly.

4. Balance Sheet:
   - Show assets vs liabilities over time.
   - Show cash if available.
   - Show liabilities as a percentage of assets.

5. Make the tab buttons actually switch between sections.
6. Keep the code beginner-readable.
7. Handle missing values as N/A instead of crashing.
8. Do not change the Flask API unless absolutely necessary.
9. Do not add the AI explanation layer yet.
10. Do not add company comparison yet.

After editing, explain what changed and how I can test each section.
```

Result: The dashboard tabs became functional, with separate tables and charts for performance, margins, and balance sheet data.

## 5. Missing Data Handling For NKE

Purpose: investigate why Nike did not show an operating margin line and make the app handle missing financial concepts honestly.

Prompt:

```text
On the Margins tab, some companies like NKE show N/A for operating margin, so the green operating margin line does not appear.

Please investigate the SEC Company Facts concepts available for NKE and improve the operating income extraction fallback logic if there is an appropriate us-gaap concept available.

Requirements:
- Do not fake or estimate operating income.
- Only use real SEC Company Facts values.
- If no appropriate operating income concept exists, keep N/A.
- If an entire chart series is missing, hide that dataset from the chart legend instead of showing a legend item with no visible line.
- Keep the code beginner-readable.
- Explain which XBRL concept was missing or added.
```

Result: The app kept Nike operating margin as `N/A` because a true operating income concept was unavailable. The frontend was updated to hide chart datasets where every value is missing.

## 6. Programmatic Key Observations

Purpose: add factual observations generated by Python calculations, not by an AI model.

Prompt:

```text
The dashboard now fetches real SEC data and handles missing chart series correctly. Next, add a programmatic Key Observations section.

Important: These observations must be generated by my Python calculations, not by AI.

Requirements:
1. In financial_metrics.py, add a function that compares the latest year with the previous year and creates factual observations such as:
   - Revenue increased or decreased by X%.
   - Net income increased or decreased by X%.
   - Net profit margin improved or declined by X percentage points.
   - Operating margin improved or declined by X percentage points, if available.
   - Liabilities as a percentage of assets increased or decreased by X percentage points, if available.

2. Include these observations in the existing API response under a key like:
   "observations": [...]

3. Each observation should be short, factual, and based only on calculated data.

4. In the frontend, add a Key Observations section below the overview/performance area.
   - It should display the observations as a clean list.
   - If observations are unavailable, show a helpful message.
   - Keep the styling consistent with the current finance-dashboard look.

5. Do not add the AI explanation layer yet.
6. Do not add company comparison yet.
7. Keep the code beginner-readable.

After editing, explain:
- where the observations are calculated
- how latest year vs previous year comparison works
- how I can test it with AAPL, MSFT, NKE, and KO
```

Result: The app added a Key Observations section based on the latest fiscal year compared with the prior fiscal year.

## 7. OpenAI Explanation Layer

Purpose: add an optional AI feature that explains the app's already-calculated metrics and observations.

Prompt:

```text
Add a real OpenAI-powered explanation feature to this Flask financial dashboard.

Important security rules:
- Do not put the OpenAI API key in frontend JavaScript.
- Do not hardcode the API key anywhere.
- Read the key from the environment variable OPENAI_API_KEY.
- If OPENAI_API_KEY is missing, return a helpful JSON error instead of crashing.
- Make sure .env remains ignored by git.

Implementation requirements:
1. Update requirements.txt to include:
   - openai
   - python-dotenv if useful for local development

2. Create a new file called ai_explainer.py.
   It should:
   - import the OpenAI Python client
   - define a function like generate_financial_explanation(dashboard_data)
   - send only structured data already calculated by my app:
     - company name
     - ticker
     - latest fiscal year
     - overview metrics
     - calculated ratios
     - programmatic observations
   - not ask the model to fetch financial data
   - not ask the model to calculate new numbers
   - instruct the model to explain the existing data in plain English
   - include a sentence that this is educational analysis, not investment advice

3. In app.py, add a backend route:
   /api/explain/<ticker>

   This route should:
   - reuse get_company_facts(ticker)
   - reuse build_dashboard_data(company_facts)
   - pass that dashboard_data into generate_financial_explanation()
   - return JSON like:
     {
       "explanation": "..."
     }

4. In the frontend:
   - Add a button labeled "Generate AI Explanation"
   - When clicked, call /api/explain/<ticker>
   - Show a loading state while waiting
   - Display the returned explanation in a clean section below Key Observations
   - Show readable errors if the API key is missing or the request fails

5. Keep the code beginner-readable.
6. Do not let AI invent numbers.
7. Do not add company comparison.
8. Do not change the SEC data calculations except if needed to pass structured data cleanly.

Use the OpenAI Responses API through the official Python SDK. Use a cost-conscious text model, and make the model name configurable with an OPENAI_MODEL environment variable.
```

Result: The app added `ai_explainer.py`, a Flask `/api/explain/<ticker>` route, and a frontend button for generating an AI explanation.

## 8. Deployment Preparation

Purpose: prepare the Flask app for Render deployment.

Prompt:

```text
Make this Flask app ready for deployment.

Please:
- Add gunicorn to requirements.txt.
- Make sure app.py can still run locally with python app.py.
- Confirm the production start command should be gunicorn app:app.
- Update README.md with deployment notes, including required environment variables:
  OPENAI_API_KEY
  OPENAI_MODEL
- Do not expose secrets.
- Do not add new features.
```

Result: The app was prepared for deployment with Gunicorn and documented Render environment variables.

## 9. Final Chart Polish

Purpose: remove Chart.js animations so the dashboard feels calmer during the demo video.

Prompt:

```text
Please remove the chart loading/transition animations from the dashboard.

Update only the frontend JavaScript unless CSS is absolutely necessary.

Requirements:
- In static/app.js, disable Chart.js animations for all charts.
- Add animation: false to the shared chart option helper functions, such as moneyChartOptions, percentChartOptions, and mixedMoneyPercentOptions.
- Also disable hover/resize transitions if Chart.js is still animating when switching tabs.
- Do not change the chart data, labels, colors, backend routes, SEC logic, or AI feature.
- The charts should appear immediately when each section opens.
- Keep the code beginner-readable.

After editing, summarize exactly what changed.
```

Result: The chart animations were disabled for a cleaner final presentation.
