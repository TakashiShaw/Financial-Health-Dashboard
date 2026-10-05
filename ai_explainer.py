"""
AI explanation helper.

This module uses the OpenAI API to explain financial data that the app has
already calculated. It does not fetch data or calculate new financial metrics.
"""

import json
import os

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


DEFAULT_MODEL = "gpt-5-mini"
DISCLAIMER = "This is educational analysis only and is not investment advice."


class AIExplainerError(Exception):
    def __init__(self, message, status_code=502):
        super().__init__(message)
        self.status_code = status_code


def generate_financial_explanation(dashboard_data):
    api_key = os.environ.get("OPENAI_API_KEY")

    if not api_key:
        raise AIExplainerError(
            "OPENAI_API_KEY is not set. Add it to your environment or local .env file.",
            status_code=400,
        )

    if OpenAI is None:
        raise AIExplainerError(
            "The OpenAI Python package is not installed. Run pip install -r requirements.txt.",
            status_code=500,
        )

    client = OpenAI(api_key=api_key)
    model = os.environ.get("OPENAI_MODEL", DEFAULT_MODEL)
    explanation_data = build_explanation_data(dashboard_data)

    try:
        response = client.responses.create(
            model=model,
            reasoning={"effort": "minimal"},
            instructions=(
                "You explain company financial dashboard data in plain English. "
                "Use only the structured data provided by the app. "
                "Do not fetch financial data. "
                "Do not calculate new numbers or invent values. "
                "If a value is missing or marked N/A, say that it is unavailable. "
                "Keep the explanation short, professional, and beginner-friendly. "
                f"Include this exact sentence: {DISCLAIMER}"
            ),
            input=(
                "Explain this calculated financial dashboard data. "
                "Use the supplied observations and metrics only:\n"
                + json.dumps(explanation_data, indent=2)
            ),
            max_output_tokens=800,
            store=False,
        )
    except Exception as error:
        raise AIExplainerError(
            f"OpenAI explanation request failed: {error}", status_code=502
        ) from error

    explanation_text = response.output_text.strip()

    if not explanation_text:
        raise AIExplainerError(
            "OpenAI returned an empty explanation. Try again or use a different OPENAI_MODEL.",
            status_code=502,
        )

    return ensure_disclaimer(explanation_text)


def build_explanation_data(dashboard_data):
    overview = dashboard_data["overview"]
    metrics = dashboard_data["metrics"]

    return {
        "companyName": dashboard_data["companyName"],
        "ticker": dashboard_data["ticker"],
        "latestFiscalYear": overview["latestYear"],
        "overviewMetrics": {
            "revenue": format_currency(overview.get("revenue")),
            "netIncome": format_currency(overview.get("netIncome")),
            "operatingIncome": format_currency(overview.get("operatingIncome")),
            "assets": format_currency(overview.get("assets")),
            "liabilities": format_currency(overview.get("liabilities")),
            "cash": format_currency(overview.get("cash")),
        },
        "calculatedRatios": {
            "revenueGrowth": format_percent(metrics.get("revenueGrowth")),
            "netProfitMargin": format_percent(metrics.get("netProfitMargin")),
            "operatingMargin": format_percent(metrics.get("operatingMargin")),
            "liabilitiesToAssets": format_percent(metrics.get("liabilitiesToAssets")),
            "returnOnAssets": format_percent(metrics.get("returnOnAssets")),
        },
        "programmaticObservations": dashboard_data.get("observations", []),
    }


def format_currency(value):
    if value is None:
        return "N/A"

    billions = value / 1_000_000_000
    return f"${billions:.1f}B"


def format_percent(value):
    if value is None:
        return "N/A"

    return f"{value * 100:.1f}%"


def ensure_disclaimer(text):
    if DISCLAIMER.lower() in text.lower():
        return text

    return f"{text}\n\n{DISCLAIMER}"
