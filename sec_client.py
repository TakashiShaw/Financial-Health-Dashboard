"""
SEC client module.

Later, this file will make requests to the SEC EDGAR Company Facts API.
For the starter MVP, it returns a small mock data set for AAPL.
"""


MOCK_COMPANY_FACTS = {
    "AAPL": {
        "ticker": "AAPL",
        "company_name": "Apple Inc.",
        "cik": "0000320193",
        "source": "Mock SEC EDGAR Company Facts data",
        "currency": "USD",
        "annual": [
            {
                "year": 2021,
                "revenue": 365_817_000_000,
                "net_income": 94_680_000_000,
                "assets": 351_002_000_000,
                "liabilities": 287_912_000_000,
            },
            {
                "year": 2022,
                "revenue": 394_328_000_000,
                "net_income": 99_803_000_000,
                "assets": 352_755_000_000,
                "liabilities": 302_083_000_000,
            },
            {
                "year": 2023,
                "revenue": 383_285_000_000,
                "net_income": 96_995_000_000,
                "assets": 352_583_000_000,
                "liabilities": 290_437_000_000,
            },
            {
                "year": 2024,
                "revenue": 391_035_000_000,
                "net_income": 93_736_000_000,
                "assets": 364_980_000_000,
                "liabilities": 308_030_000_000,
            },
        ],
    }
}


def get_company_facts(ticker):
    """Return mock company facts for a ticker symbol."""
    cleaned_ticker = ticker.strip().upper()
    return MOCK_COMPANY_FACTS.get(cleaned_ticker)
