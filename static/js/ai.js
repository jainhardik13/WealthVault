// AI Prediction Modal
let aiPredictionModal = null;

async function showAIPrediction(symbol) {
    // Create modal if it doesn't exist
    if (!aiPredictionModal) {
        aiPredictionModal = document.createElement('div');
        aiPredictionModal.className = 'modal';
        aiPredictionModal.id = 'aiModal';
        aiPredictionModal.innerHTML = `
            <div class="modal-content">
                <span class="close" onclick="closeAIModal()">&times;</span>
                <h2>AI Stock Analysis</h2>
                <div id="aiContent">
                    <p>Loading AI analysis...</p>
                </div>
            </div>
        `;
        document.body.appendChild(aiPredictionModal);
    }

    // Show modal
    aiPredictionModal.style.display = 'block';

    // Fetch AI prediction
    try {
        const response = await fetch(`/ai/predict/${symbol}`);
        const data = await response.json();

        if (data.error) {
            document.getElementById('aiContent').innerHTML = `
                <p class="error">${data.error}</p>
            `;
            return;
        }

        // Display AI prediction
        document.getElementById('aiContent').innerHTML = `
            <h3>${symbol}</h3>
            <div class="ai-result">
                <p><strong>Summary:</strong> ${data.summary}</p>
                <p><strong>Trend:</strong> <span class="badge ${data.trend.toLowerCase()}">${data.trend}</span></p>
                <p><strong>Risk Level:</strong> <span class="badge ${data.risk.toLowerCase()}">${data.risk}</span></p>
                <p><strong>Recommendation:</strong> <span class="badge ${data.recommendation.toLowerCase()}">${data.recommendation}</span></p>
                <p><strong>Reasoning:</strong> ${data.reasoning}</p>
                <p class="disclaimer">⚠️ This is for educational purposes only, not financial advice.</p>
            </div>
        `;
    } catch (error) {
        console.error('AI prediction error:', error);
        document.getElementById('aiContent').innerHTML = `
            <p class="error">Failed to load AI prediction. Please try again.</p>
        `;
    }
}

function closeAIModal() {
    if (aiPredictionModal) {
        aiPredictionModal.style.display = 'none';
    }
}

// Portfolio AI Insights
async function showPortfolioInsights() {
    // Calculate portfolio totals
    const stocks = Array.from(document.querySelectorAll('table tr')).slice(1); // Skip header
    let totalInvested = 0;
    let currentValue = 0;

    stocks.forEach(row => {
        const cells = row.cells;
        if (cells && cells.length > 3) {
            const quantity = parseFloat(cells[1].textContent) || 0;
            const buyPrice = parseFloat(cells[2].textContent) || 0;
            const currentPrice = parseFloat(cells[3].textContent) || 0;

            totalInvested += quantity * buyPrice;
            currentValue += quantity * currentPrice;
        }
    });

    const totalProfit = currentValue - totalInvested;
    const profitPercent = totalInvested > 0 ? (totalProfit / totalInvested) * 100 : 0;

    // Create modal for portfolio insights
    if (!document.getElementById('portfolioAIModal')) {
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.id = 'portfolioAIModal';
        modal.innerHTML = `
            <div class="modal-content">
                <span class="close" onclick="closePortfolioAIModal()">&times;</span>
                <h2>Portfolio AI Insights</h2>
                <div id="portfolioAIContent">
                    <p>Loading insights...</p>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
    }

    document.getElementById('portfolioAIModal').style.display = 'block';

    // Fetch AI insights
    try {
        const response = await fetch('/ai/portfolio-insights', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                total_invested: totalInvested,
                current_value: currentValue,
                total_profit: totalProfit,
                profit_percent: profitPercent
            })
        });

        const data = await response.json();

        document.getElementById('portfolioAIContent').innerHTML = `
            <div class="ai-result">
                <p><strong>Assessment:</strong> ${data.assessment}</p>
                <p><strong>Risk Level:</strong> <span class="badge ${data.risk.toLowerCase()}">${data.risk}</span></p>
                <p><strong>Suggestion:</strong> ${data.suggestion}</p>
                <p class="disclaimer">⚠️ This is for educational purposes only, not financial advice.</p>
            </div>
        `;
    } catch (error) {
        console.error('Portfolio AI error:', error);
        document.getElementById('portfolioAIContent').innerHTML = `
            <p class="error">Failed to load insights. Please try again.</p>
        `;
    }
}

function closePortfolioAIModal() {
    const modal = document.getElementById('portfolioAIModal');
    if (modal) {
        modal.style.display = 'none';
    }
}
