"""
SEC client module.

This file handles the network requests to SEC EDGAR:
1. Look up a ticker symbol in SEC's company ticker list.
2. Convert the company's CIK to the 10-digit SEC format.
3. Fetch the company's XBRL Company Facts JSON.
"""

import json
import os
import ssl
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


COMPANY_TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
COMPANY_FACTS_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"

# SEC asks automated tools to identify themselves with a clear User-Agent.
# You can set SEC_USER_AGENT in your terminal if you want to use your own contact.
SEC_USER_AGENT = os.environ.get(
    "SEC_USER_AGENT",
    "CMU-15-113-Financial-Health-Dashboard/1.0 student-contact@example.com",
)

_ticker_cache = None


class SecClientError(Exception):
    def __init__(self, message, status_code=502):
        super().__init__(message)
        self.status_code = status_code


def fetch_json(url):
    """Fetch a JSON URL from SEC and return it as a Python dictionary."""
    request = Request(
        url,
        headers={
            "User-Agent": SEC_USER_AGENT,
            "Accept": "application/json",
        },
    )

    try:
        with urlopen(request, timeout=20, context=get_ssl_context()) as response:
            response_text = response.read().decode("utf-8")
            return json.loads(response_text)
    except HTTPError as error:
        raise SecClientError(
            f"SEC request failed with status {error.code}. Please try again later.",
            status_code=502,
        ) from error
    except URLError as error:
        raise SecClientError(
            f"Could not connect to SEC EDGAR: {error.reason}", status_code=502
        ) from error
    except json.JSONDecodeError as error:
        raise SecClientError(
            "SEC returned data that could not be read as JSON.", status_code=502
        ) from error


def get_ssl_context():
    """Use the system certificate bundle when this Python install needs it."""
    if os.path.exists("/etc/ssl/cert.pem"):
        return ssl.create_default_context(cafile="/etc/ssl/cert.pem")

    return ssl.create_default_context()


def get_company_tickers():
    """Return SEC's ticker lookup data, using a small in-memory cache."""
    global _ticker_cache

    if _ticker_cache is None:
        _ticker_cache = fetch_json(COMPANY_TICKERS_URL)

    return _ticker_cache


def clean_ticker(ticker):
    return ticker.strip().upper()


def format_cik(cik):
    """SEC Company Facts URLs require a 10-digit, zero-padded CIK."""
    return str(cik).zfill(10)


def find_company_by_ticker(ticker):
    """Find one company record from SEC's ticker lookup JSON."""
    cleaned_ticker = clean_ticker(ticker)

    if cleaned_ticker == "":
        raise SecClientError("Please enter a ticker symbol.", status_code=400)

    company_tickers = get_company_tickers()

    for company in company_tickers.values():
        if company.get("ticker", "").upper() == cleaned_ticker:
            return company

    raise SecClientError(
        f"Ticker '{cleaned_ticker}' was not found in SEC's company ticker list.",
        status_code=404,
    )


def get_company_facts(ticker):
    """Return raw SEC Company Facts data plus simple company metadata."""
    company = find_company_by_ticker(ticker)
    cik = format_cik(company["cik_str"])
    company_facts_url = COMPANY_FACTS_URL.format(cik=cik)
    company_facts_json = fetch_json(company_facts_url)

    if "facts" not in company_facts_json:
        raise SecClientError(
            "SEC Company Facts data did not include financial facts.",
            status_code=502,
        )

    return {
        "ticker": company["ticker"].upper(),
        "company_name": company.get("title", company_facts_json.get("entityName")),
        "cik": cik,
        "source": "SEC EDGAR Company Facts API",
        "currency": "USD",
        "raw_facts": company_facts_json,
    }
