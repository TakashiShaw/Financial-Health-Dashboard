from flask import Flask, jsonify, render_template

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv():
        return False

from ai_explainer import AIExplainerError, generate_financial_explanation
from financial_metrics import FinancialDataError, build_dashboard_data
from sec_client import SecClientError, get_company_facts


load_dotenv()

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


@app.route("/api/explain/<ticker>")
def explain_api(ticker):
    try:
        company_facts = get_company_facts(ticker)
        dashboard_data = build_dashboard_data(company_facts)
        explanation = generate_financial_explanation(dashboard_data)
        return jsonify({"explanation": explanation})
    except SecClientError as error:
        return jsonify({"error": str(error)}), error.status_code
    except FinancialDataError as error:
        return jsonify({"error": str(error)}), 422
    except AIExplainerError as error:
        return jsonify({"error": str(error)}), error.status_code


if __name__ == "__main__":
    app.run(debug=True, port=5001)
