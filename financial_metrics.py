"""
Financial metric calculations.

These functions are intentionally simple so the project is easy to explain.
"""


def safe_divide(numerator, denominator):
    if denominator == 0:
        return 0
    return numerator / denominator


def calculate_profit_margin(net_income, revenue):
    return safe_divide(net_income, revenue)


def calculate_debt_to_assets(liabilities, assets):
    return safe_divide(liabilities, assets)


def calculate_return_on_assets(net_income, assets):
    return safe_divide(net_income, assets)


def build_dashboard_data(company_facts):
    annual_data = company_facts["annual"]
    latest_year = annual_data[-1]

    profit_margin = calculate_profit_margin(
        latest_year["net_income"], latest_year["revenue"]
    )
    debt_to_assets = calculate_debt_to_assets(
        latest_year["liabilities"], latest_year["assets"]
    )
    return_on_assets = calculate_return_on_assets(
        latest_year["net_income"], latest_year["assets"]
    )

    return {
        "ticker": company_facts["ticker"],
        "companyName": company_facts["company_name"],
        "cik": company_facts["cik"],
        "source": company_facts["source"],
        "currency": company_facts["currency"],
        "overview": {
            "latestYear": latest_year["year"],
            "revenue": latest_year["revenue"],
            "netIncome": latest_year["net_income"],
            "assets": latest_year["assets"],
            "liabilities": latest_year["liabilities"],
        },
        "metrics": {
            "profitMargin": profit_margin,
            "debtToAssets": debt_to_assets,
            "returnOnAssets": return_on_assets,
        },
        "annualData": annual_data,
    }
