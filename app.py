from flask import Flask, jsonify, render_template

from financial_metrics import FinancialDataError, build_dashboard_data
from sec_client import SecClientError, get_company_facts


app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/company/<ticker>")
def company_api(ticker):
    try:
        company_facts = get_company_facts(ticker)
        dashboard_data = build_dashboard_data(company_facts)
        return jsonify(dashboard_data)
    except SecClientError as error:
        return jsonify({"error": str(error)}), error.status_code
    except FinancialDataError as error:
        return jsonify({"error": str(error)}), 422


if __name__ == "__main__":
    app.run(debug=True, port=5001)
