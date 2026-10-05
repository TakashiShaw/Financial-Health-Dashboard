from flask import Flask, jsonify, render_template

from financial_metrics import build_dashboard_data
from sec_client import get_company_facts


app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/company/<ticker>")
def company_api(ticker):
    company_facts = get_company_facts(ticker)

    if company_facts is None:
        return (
            jsonify(
                {
                    "error": "Mock data is only available for AAPL right now. SEC integration comes next."
                }
            ),
            404,
        )

    dashboard_data = build_dashboard_data(company_facts)
    return jsonify(dashboard_data)


if __name__ == "__main__":
    app.run(debug=True, port=5001)
