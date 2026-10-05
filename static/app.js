let charts = {};
let activeSection = "overview";

const form = document.querySelector("#search-form");
const tickerInput = document.querySelector("#ticker-input");
const message = document.querySelector("#message");
const tabButtons = document.querySelectorAll(".tab-button");

form.addEventListener("submit", function (event) {
    event.preventDefault();
    loadCompany(tickerInput.value);
});

tabButtons.forEach(function (button) {
    button.addEventListener("click", function () {
        switchSection(button.dataset.section);
    });
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

function switchSection(sectionName) {
    activeSection = sectionName;

    tabButtons.forEach(function (button) {
        button.classList.toggle("active-tab", button.dataset.section === sectionName);
    });

    document.querySelectorAll(".tab-panel").forEach(function (panel) {
        panel.classList.toggle("active-panel", panel.id === `${sectionName}-panel`);
    });

    if (charts[sectionName]) {
        charts[sectionName].resize();
    }
}

function renderDashboard(data) {
    document.querySelector("#company-name").textContent = data.companyName;
    document.querySelector("#ticker-badge").textContent = data.ticker;
    document.querySelector("#company-details").textContent = `CIK ${data.cik} | Latest fiscal year: ${data.overview.latestYear}`;
    document.querySelector("#data-source").textContent = data.source;

    renderOverview(data);
    renderPerformance(data.annualData);
    renderMargins(data.annualData);
    renderBalanceSheet(data.annualData);
    renderCharts(data.annualData);
    switchSection(activeSection);
}

function renderOverview(data) {
    const latestYear = data.overview.latestYear;

    document.querySelector("#revenue-year").textContent = latestYear;
    document.querySelector("#net-income-year").textContent = latestYear;
    document.querySelector("#profit-margin-year").textContent = latestYear;
    document.querySelector("#debt-assets-year").textContent = latestYear;

    document.querySelector("#revenue-card").textContent = formatCurrency(data.overview.revenue);
    document.querySelector("#net-income-card").textContent = formatCurrency(data.overview.netIncome);
    document.querySelector("#profit-margin-card").textContent = formatPercent(data.metrics.profitMargin);
    document.querySelector("#debt-assets-card").textContent = formatPercent(data.metrics.debtToAssets);
}

function renderPerformance(annualData) {
    const rows = annualData.map(function (yearData) {
        return [
            yearData.year,
            formatCurrency(yearData.revenue),
            formatCurrency(yearData.net_income),
            formatPercent(yearData.revenue_growth),
        ];
    });

    fillTable("#performance-table-body", rows);
}

function renderMargins(annualData) {
    const rows = annualData.map(function (yearData) {
        return [
            yearData.year,
            formatPercent(yearData.profit_margin),
            formatPercent(yearData.operating_margin),
        ];
    });

    fillTable("#margins-table-body", rows);
}

function renderBalanceSheet(annualData) {
    const rows = annualData.map(function (yearData) {
        return [
            yearData.year,
            formatCurrency(yearData.assets),
            formatCurrency(yearData.liabilities),
            formatCurrency(yearData.cash),
            formatPercent(yearData.liabilities_to_assets),
        ];
    });

    fillTable("#balance-table-body", rows);
}

function fillTable(selector, rows) {
    const tableBody = document.querySelector(selector);
    tableBody.innerHTML = "";

    rows.forEach(function (row) {
        const tableRow = document.createElement("tr");

        row.forEach(function (cellValue) {
            const cell = document.createElement("td");
            cell.textContent = cellValue;
            tableRow.appendChild(cell);
        });

        tableBody.appendChild(tableRow);
    });
}

function renderCharts(annualData) {
    destroyCharts();

    renderOverviewChart(annualData);
    renderPerformanceChart(annualData);
    renderMarginsChart(annualData);
    renderBalanceChart(annualData);
}

function destroyCharts() {
    Object.values(charts).forEach(function (chart) {
        chart.destroy();
    });

    charts = {};
}

function renderOverviewChart(annualData) {
    charts.overview = new Chart(document.querySelector("#overview-chart"), {
        type: "bar",
        data: {
            labels: getYears(annualData),
            datasets: filterMissingDatasets([
                {
                    label: "Revenue",
                    data: annualData.map((yearData) => toBillions(yearData.revenue)),
                    backgroundColor: "#25735f",
                },
                {
                    label: "Net Income",
                    data: annualData.map((yearData) => toBillions(yearData.net_income)),
                    backgroundColor: "#2563eb",
                },
            ]),
        },
        options: moneyChartOptions("USD billions"),
    });
}

function renderPerformanceChart(annualData) {
    charts.performance = new Chart(document.querySelector("#performance-chart"), {
        type: "bar",
        data: {
            labels: getYears(annualData),
            datasets: filterMissingDatasets([
                {
                    type: "bar",
                    label: "Revenue",
                    data: annualData.map((yearData) => toBillions(yearData.revenue)),
                    backgroundColor: "#25735f",
                    yAxisID: "money",
                },
                {
                    type: "bar",
                    label: "Net Income",
                    data: annualData.map((yearData) => toBillions(yearData.net_income)),
                    backgroundColor: "#2563eb",
                    yAxisID: "money",
                },
                {
                    type: "line",
                    label: "Revenue Growth",
                    data: annualData.map((yearData) => toPercentNumber(yearData.revenue_growth)),
                    borderColor: "#a16207",
                    backgroundColor: "#a16207",
                    tension: 0.2,
                    yAxisID: "percent",
                },
            ]),
        },
        options: mixedMoneyPercentOptions("USD billions", "Revenue growth"),
    });
}

function renderMarginsChart(annualData) {
    charts.margins = new Chart(document.querySelector("#margins-chart"), {
        type: "line",
        data: {
            labels: getYears(annualData),
            datasets: filterMissingDatasets([
                {
                    label: "Net Profit Margin",
                    data: annualData.map((yearData) => toPercentNumber(yearData.profit_margin)),
                    borderColor: "#2563eb",
                    backgroundColor: "#2563eb",
                    tension: 0.2,
                },
                {
                    label: "Operating Margin",
                    data: annualData.map((yearData) => toPercentNumber(yearData.operating_margin)),
                    borderColor: "#25735f",
                    backgroundColor: "#25735f",
                    tension: 0.2,
                },
            ]),
        },
        options: percentChartOptions("Margin"),
    });
}

function renderBalanceChart(annualData) {
    charts.balance = new Chart(document.querySelector("#balance-chart"), {
        type: "bar",
        data: {
            labels: getYears(annualData),
            datasets: filterMissingDatasets([
                {
                    type: "bar",
                    label: "Assets",
                    data: annualData.map((yearData) => toBillions(yearData.assets)),
                    backgroundColor: "#25735f",
                    yAxisID: "money",
                },
                {
                    type: "bar",
                    label: "Liabilities",
                    data: annualData.map((yearData) => toBillions(yearData.liabilities)),
                    backgroundColor: "#64748b",
                    yAxisID: "money",
                },
                {
                    type: "bar",
                    label: "Cash",
                    data: annualData.map((yearData) => toBillions(yearData.cash)),
                    backgroundColor: "#93c5fd",
                    yAxisID: "money",
                },
                {
                    type: "line",
                    label: "Liabilities / Assets",
                    data: annualData.map((yearData) => toPercentNumber(yearData.liabilities_to_assets)),
                    borderColor: "#a16207",
                    backgroundColor: "#a16207",
                    tension: 0.2,
                    yAxisID: "percent",
                },
            ]),
        },
        options: mixedMoneyPercentOptions("USD billions", "Liabilities / Assets"),
    });
}

function getYears(annualData) {
    return annualData.map(function (yearData) {
        return yearData.year;
    });
}

function toBillions(value) {
    if (value === null || value === undefined || Number.isNaN(value)) {
        return null;
    }

    return value / 1_000_000_000;
}

function toPercentNumber(value) {
    if (value === null || value === undefined || Number.isNaN(value)) {
        return null;
    }

    return value * 100;
}

function filterMissingDatasets(datasets) {
    return datasets.filter(function (dataset) {
        return dataset.data.some(function (value) {
            return value !== null && value !== undefined && !Number.isNaN(value);
        });
    });
}

function moneyChartOptions(yAxisTitle) {
    return {
        maintainAspectRatio: false,
        responsive: true,
        plugins: {
            tooltip: {
                callbacks: {
                    label: function (context) {
                        return `${context.dataset.label}: ${formatChartCurrency(context.raw)}`;
                    },
                },
            },
        },
        scales: {
            y: {
                beginAtZero: true,
                title: {
                    display: true,
                    text: yAxisTitle,
                },
            },
        },
    };
}

function percentChartOptions(yAxisTitle) {
    return {
        maintainAspectRatio: false,
        responsive: true,
        plugins: {
            tooltip: {
                callbacks: {
                    label: function (context) {
                        return `${context.dataset.label}: ${formatChartPercent(context.raw)}`;
                    },
                },
            },
        },
        scales: {
            y: {
                title: {
                    display: true,
                    text: yAxisTitle,
                },
                ticks: {
                    callback: function (value) {
                        return `${value}%`;
                    },
                },
            },
        },
    };
}

function mixedMoneyPercentOptions(moneyTitle, percentTitle) {
    return {
        maintainAspectRatio: false,
        responsive: true,
        interaction: {
            mode: "index",
            intersect: false,
        },
        plugins: {
            tooltip: {
                callbacks: {
                    label: function (context) {
                        if (context.dataset.yAxisID === "percent") {
                            return `${context.dataset.label}: ${formatChartPercent(context.raw)}`;
                        }

                        return `${context.dataset.label}: ${formatChartCurrency(context.raw)}`;
                    },
                },
            },
        },
        scales: {
            money: {
                beginAtZero: true,
                position: "left",
                title: {
                    display: true,
                    text: moneyTitle,
                },
            },
            percent: {
                position: "right",
                grid: {
                    drawOnChartArea: false,
                },
                title: {
                    display: true,
                    text: percentTitle,
                },
                ticks: {
                    callback: function (value) {
                        return `${value}%`;
                    },
                },
            },
        },
    };
}

function formatCurrency(value) {
    if (value === null || value === undefined || Number.isNaN(value)) {
        return "N/A";
    }

    const billions = value / 1_000_000_000;
    return `$${billions.toFixed(1)}B`;
}

function formatPercent(value) {
    if (value === null || value === undefined || Number.isNaN(value)) {
        return "N/A";
    }

    return `${(value * 100).toFixed(1)}%`;
}

function formatChartCurrency(value) {
    if (value === null || value === undefined || Number.isNaN(value)) {
        return "N/A";
    }

    return `$${value.toFixed(1)}B`;
}

function formatChartPercent(value) {
    if (value === null || value === undefined || Number.isNaN(value)) {
        return "N/A";
    }

    return `${value.toFixed(1)}%`;
}

function showMessage(text) {
    message.textContent = text;
}

loadCompany("AAPL");
