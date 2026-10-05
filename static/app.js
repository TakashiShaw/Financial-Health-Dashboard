let financialChart = null;

const form = document.querySelector("#search-form");
const tickerInput = document.querySelector("#ticker-input");
const message = document.querySelector("#message");

form.addEventListener("submit", function (event) {
    event.preventDefault();
    loadCompany(tickerInput.value);
});

async function loadCompany(ticker) {
    const cleanedTicker = ticker.trim().toUpperCase();

    if (cleanedTicker === "") {
        showMessage("Please enter a ticker symbol.");
        return;
    }

    showMessage("");

    try {
        const response = await fetch(`/api/company/${cleanedTicker}`);
        const data = await response.json();

        if (!response.ok) {
            showMessage(data.error || "Something went wrong.");
            return;
        }

        renderDashboard(data);
    } catch (error) {
        showMessage("Could not reach the Flask server.");
    }
}

function renderDashboard(data) {
    document.querySelector("#company-name").textContent = data.companyName;
    document.querySelector("#ticker-badge").textContent = data.ticker;
    document.querySelector("#company-details").textContent = `CIK ${data.cik} | Latest fiscal year: ${data.overview.latestYear}`;
    document.querySelector("#data-source").textContent = data.source;

    document.querySelector("#revenue-year").textContent = data.overview.latestYear;
    document.querySelector("#net-income-year").textContent = data.overview.latestYear;
    document.querySelector("#profit-margin-year").textContent = data.overview.latestYear;
    document.querySelector("#debt-assets-year").textContent = data.overview.latestYear;

    document.querySelector("#revenue-card").textContent = formatCurrency(data.overview.revenue);
    document.querySelector("#net-income-card").textContent = formatCurrency(data.overview.netIncome);
    document.querySelector("#profit-margin-card").textContent = formatPercent(data.metrics.profitMargin);
    document.querySelector("#debt-assets-card").textContent = formatPercent(data.metrics.debtToAssets);

    renderChart(data.annualData);
}

function renderChart(annualData) {
    const chartCanvas = document.querySelector("#financial-chart");
    const years = annualData.map((yearData) => yearData.year);
    const revenue = annualData.map((yearData) => yearData.revenue / 1_000_000_000);
    const netIncome = annualData.map((yearData) => yearData.net_income / 1_000_000_000);

    if (financialChart !== null) {
        financialChart.destroy();
    }

    financialChart = new Chart(chartCanvas, {
        type: "bar",
        data: {
            labels: years,
            datasets: [
                {
                    label: "Revenue",
                    data: revenue,
                    backgroundColor: "#0f766e",
                },
                {
                    label: "Net Income",
                    data: netIncome,
                    backgroundColor: "#2563eb",
                },
            ],
        },
        options: {
            maintainAspectRatio: false,
            responsive: true,
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            return `${context.dataset.label}: $${context.raw.toFixed(1)}B`;
                        },
                    },
                },
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: "USD billions",
                    },
                },
            },
        },
    });
}

function formatCurrency(value) {
    const billions = value / 1_000_000_000;
    return `$${billions.toFixed(1)}B`;
}

function formatPercent(value) {
    return `${(value * 100).toFixed(1)}%`;
}

function showMessage(text) {
    message.textContent = text;
}

loadCompany("AAPL");
