"""
Financial metric calculations.

This file turns raw SEC Company Facts JSON into the simpler dashboard JSON
that the frontend uses.
"""

from datetime import date


CONCEPTS = {
    # Companies do not always use the same XBRL tag for the same idea.
    # Each list starts with the preferred tag, then tries fallback tags.
    "revenue": [
        "RevenueFromContractWithCustomerExcludingAssessedTax",
        "Revenues",
        "SalesRevenueNet",
        "SalesRevenueGoodsNet",
        "SalesRevenueServicesNet",
        "OperatingRevenues",
    ],
    "net_income": [
        "NetIncomeLoss",
        "ProfitLoss",
        "NetIncomeLossAvailableToCommonStockholdersBasic",
    ],
    "operating_income": [
        # Only include concepts that directly mean operating income.
        # Do not use pretax income concepts as a substitute.
        "OperatingIncomeLoss",
    ],
    "assets": [
        "Assets",
    ],
    "liabilities": [
        "Liabilities",
    ],
    "cash": [
        "CashAndCashEquivalentsAtCarryingValue",
        "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents",
        "Cash",
    ],
}


class FinancialDataError(Exception):
    pass


def safe_divide(numerator, denominator):
    """Return None instead of crashing when a ratio cannot be calculated."""
    if numerator is None or denominator in (None, 0):
        return None
    return numerator / denominator


def calculate_growth(current_value, previous_value):
    return safe_divide(current_value - previous_value, previous_value)


def format_percent_change(value):
    return f"{abs(value) * 100:.1f}%"


def format_percentage_points(value):
    return f"{abs(value) * 100:.1f} percentage points"


def describe_value_change(metric_name, latest_value, previous_value, latest_year, previous_year):
    change = calculate_growth(latest_value, previous_value)

    if change is None:
        return None

    if change > 0:
        return (
            f"{metric_name} increased by {format_percent_change(change)} "
            f"from {previous_year} to {latest_year}."
        )

    if change < 0:
        return (
            f"{metric_name} decreased by {format_percent_change(change)} "
            f"from {previous_year} to {latest_year}."
        )

    return f"{metric_name} was unchanged from {previous_year} to {latest_year}."


def describe_ratio_change(
    metric_name,
    latest_ratio,
    previous_ratio,
    latest_year,
    previous_year,
    positive_word,
    negative_word,
):
    if latest_ratio is None or previous_ratio is None:
        return None

    change = latest_ratio - previous_ratio

    if change > 0:
        return (
            f"{metric_name} {positive_word} by {format_percentage_points(change)} "
            f"from {previous_year} to {latest_year}."
        )

    if change < 0:
        return (
            f"{metric_name} {negative_word} by {format_percentage_points(change)} "
            f"from {previous_year} to {latest_year}."
        )

    return f"{metric_name} was unchanged from {previous_year} to {latest_year}."


def build_observations(annual_data):
    """Create short factual observations from the latest two annual rows."""
    if len(annual_data) < 2:
        return []

    # The observations compare the newest year with the year immediately before
    # it. This keeps the text factual and explainable.
    previous_year = annual_data[-2]
    latest_year = annual_data[-1]
    observations = []

    revenue_observation = describe_value_change(
        "Revenue",
        latest_year["revenue"],
        previous_year["revenue"],
        latest_year["year"],
        previous_year["year"],
    )
    net_income_observation = describe_value_change(
        "Net income",
        latest_year["net_income"],
        previous_year["net_income"],
        latest_year["year"],
        previous_year["year"],
    )
    profit_margin_observation = describe_ratio_change(
        "Net profit margin",
        latest_year["profit_margin"],
        previous_year["profit_margin"],
        latest_year["year"],
        previous_year["year"],
        "improved",
        "declined",
    )
    operating_margin_observation = describe_ratio_change(
        "Operating margin",
        latest_year["operating_margin"],
        previous_year["operating_margin"],
        latest_year["year"],
        previous_year["year"],
        "improved",
        "declined",
    )
    liabilities_observation = describe_ratio_change(
        "Liabilities as a percentage of assets",
        latest_year["liabilities_to_assets"],
        previous_year["liabilities_to_assets"],
        latest_year["year"],
        previous_year["year"],
        "increased",
        "decreased",
    )

    for observation in [
        revenue_observation,
        net_income_observation,
        profit_margin_observation,
        operating_margin_observation,
        liabilities_observation,
    ]:
        if observation is not None:
            observations.append(observation)

    return observations


def is_annual_10k_fact(fact):
    """Return True for annual 10-K facts and skip quarterly/interim facts."""
    form = (fact.get("form") or "").upper()
    fiscal_period = (fact.get("fp") or "").upper()

    return (
        form.startswith("10-K")
        and fiscal_period == "FY"
        and fact.get("fy") is not None
        and fact.get("val") is not None
        and is_annual_period(fact)
    )


def is_annual_period(fact):
    """For duration facts, keep periods that are about one year long."""
    start = fact.get("start")
    end = fact.get("end")

    if start is None or end is None:
        return True

    try:
        start_date = date.fromisoformat(start)
        end_date = date.fromisoformat(end)
    except ValueError:
        return True

    days = (end_date - start_date).days
    return 330 <= days <= 380


def get_fact_year(fact):
    """Use the fact's period end date as the dashboard year."""
    end = fact.get("end")

    if isinstance(end, str) and len(end) >= 4 and end[:4].isdigit():
        return int(end[:4])

    frame = fact.get("frame") or ""
    if frame.startswith("CY") and frame[2:6].isdigit():
        return int(frame[2:6])

    return int(fact["fy"])


def get_us_gaap_facts(company_facts):
    raw_facts = company_facts["raw_facts"]
    facts = raw_facts.get("facts", {})
    us_gaap = facts.get("us-gaap", {})

    if not us_gaap:
        raise FinancialDataError("SEC data did not include us-gaap facts.")

    return us_gaap


def latest_annual_fact_by_year(facts):
    """Keep the latest filed 10-K fact for each fiscal year."""
    latest_by_year = {}

    for fact in facts:
        if not is_annual_10k_fact(fact):
            continue

        year = get_fact_year(fact)
        current_latest = latest_by_year.get(year)

        if current_latest is None or fact.get("filed", "") > current_latest.get(
            "filed", ""
        ):
            latest_by_year[year] = fact

    return latest_by_year


def extract_concept_series(us_gaap, concept_names):
    """
    Try several possible XBRL concept names and return values by fiscal year.

    The first concept in the list is preferred, but later concepts can fill gaps.
    """
    values_by_year = {}

    for concept_name in concept_names:
        concept = us_gaap.get(concept_name)

        if concept is None:
            continue

        usd_facts = concept.get("units", {}).get("USD", [])
        annual_facts = latest_annual_fact_by_year(usd_facts)

        # Earlier concept names have priority. Fallback concepts only fill
        # years that are still missing.
        for year, fact in annual_facts.items():
            if year not in values_by_year:
                values_by_year[year] = fact["val"]

    return values_by_year


def build_annual_rows(series_by_metric):
    """Combine separate metric series into one row per fiscal year."""
    all_years = sorted(
        {
            year
            for metric_series in series_by_metric.values()
            for year in metric_series.keys()
        }
    )

    rows = []
    previous_revenue = None

    for year in all_years:
        revenue = series_by_metric["revenue"].get(year)
        net_income = series_by_metric["net_income"].get(year)
        operating_income = series_by_metric["operating_income"].get(year)
        assets = series_by_metric["assets"].get(year)
        liabilities = series_by_metric["liabilities"].get(year)
        cash = series_by_metric["cash"].get(year)

        if revenue is None or net_income is None:
            continue

        # Values stay as raw dollars in the API. The frontend converts them to
        # billions only for display.
        row = {
            "year": year,
            "revenue": revenue,
            "net_income": net_income,
            "operating_income": operating_income,
            "assets": assets,
            "liabilities": liabilities,
            "cash": cash,
            "revenue_growth": calculate_growth(revenue, previous_revenue)
            if previous_revenue is not None
            else None,
            "profit_margin": safe_divide(net_income, revenue),
            "operating_margin": safe_divide(operating_income, revenue),
            "liabilities_to_assets": safe_divide(liabilities, assets),
        }

        rows.append(row)
        previous_revenue = revenue

    return rows


def build_dashboard_data(company_facts):
    """Create the final JSON shape consumed by static/app.js."""
    us_gaap = get_us_gaap_facts(company_facts)

    series_by_metric = {}
    for metric_name, concept_names in CONCEPTS.items():
        series_by_metric[metric_name] = extract_concept_series(us_gaap, concept_names)

    annual_data = build_annual_rows(series_by_metric)

    if not annual_data:
        raise FinancialDataError(
            "Could not find annual 10-K revenue and net income data for this company."
        )

    latest_year = annual_data[-1]

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
            "operatingIncome": latest_year["operating_income"],
            "assets": latest_year["assets"],
            "liabilities": latest_year["liabilities"],
            "cash": latest_year["cash"],
        },
        "metrics": {
            "revenueGrowth": latest_year["revenue_growth"],
            "profitMargin": latest_year["profit_margin"],
            "netProfitMargin": latest_year["profit_margin"],
            "operatingMargin": latest_year["operating_margin"],
            "debtToAssets": latest_year["liabilities_to_assets"],
            "liabilitiesToAssets": latest_year["liabilities_to_assets"],
            "returnOnAssets": safe_divide(
                latest_year["net_income"], latest_year["assets"]
            ),
        },
        "observations": build_observations(annual_data),
        "annualData": annual_data,
    }
