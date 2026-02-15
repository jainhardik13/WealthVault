document.addEventListener("DOMContentLoaded", () => {
    const input = document.getElementById("symbolInput");
    const resultBox = document.getElementById("searchResults");

//     if not on dashboard page exit safely
    if (!input || !resultBox) return;

    input.addEventListener("input", async () => {
        const query = input.value.trim();

        if (query.length < 2) {
            resultBox.innerHTML = "";
            return;
        }

        try {
            const response = await fetch(`/search?q=${query}`);
            const data = await response.json();

            resultBox.innerHTML = "";

            data.forEach(symbol => {
                const li = document.createElement("li");
                li.innerHTML = `<span class="symbol-name">${symbol}</span><span class="loading-price">Loading...</span>`;
                li.style.cursor = "pointer";

                // Fetch live price for this symbol
                fetchLivePrice(symbol, li);

                li.onclick = () => {
                    input.value = symbol;
                    resultBox.innerHTML = "";
                };

                resultBox.appendChild(li);
            });
        } catch (err) {
            console.error("Search error:", err);
        }
    });
});

async function fetchLivePrice(symbol, listItem) {
    try {
        const response = await fetch(`/stock/live/${symbol}`);
        const data = await response.json();

        if (data.success) {
            const priceSpan = listItem.querySelector('.loading-price');
            const changeClass = data.change >= 0 ? 'positive' : 'negative';
            const changeSymbol = data.change >= 0 ? '+' : '';

            priceSpan.innerHTML = `
                <span class="price">₹${data.price}</span>
                <span class="${changeClass}">${changeSymbol}${data.change_percent}%</span>
            `;
            priceSpan.classList.remove('loading-price');
            priceSpan.classList.add('stock-price-info');
        } else {
            const priceSpan = listItem.querySelector('.loading-price');
            priceSpan.textContent = 'N/A';
        }
    } catch (err) {
        console.error(`Error fetching price for ${symbol}:`, err);
        const priceSpan = listItem.querySelector('.loading-price');
        if (priceSpan) {
            priceSpan.textContent = 'N/A';
        }
    }
}