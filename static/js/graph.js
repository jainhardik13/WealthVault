let chartInstance = null;

async function openGraph(symbol) {
    const modal = document.getElementById("graphModal");
    modal.style.display = "block";

    const response = await fetch(
        `/stock/history/${symbol}`
    );

    const data = await response.json();

    // 🔥 SAFETY CHECK
    if (!data || !data.dates || !data.prices) {
        alert("Price history not available for this stock.");
        return;
    }

    const ctx = document.getElementById("stockChart").getContext("2d");

    if (chartInstance) {
        chartInstance.destroy();
    }

    chartInstance = new Chart(ctx, {
        type: "line",
        data: {
            labels: data.dates,
            datasets: [{
                label: `${symbol} Price`,
                data: data.prices,
                borderWidth: 2,
                tension: 0.3
            }]
        }
    });
}

function closeGraph() {
    document.getElementById("graphModal").style.display = "none";
}