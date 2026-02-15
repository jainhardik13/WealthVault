from flask import Blueprint, request, jsonify
from services.ai_service import get_stock_prediction, get_portfolio_insights
from services.stock_service import get_stock_details

ai_bp = Blueprint('ai', __name__)


@ai_bp.route("/ai/predict/<symbol>")
def predict_stock(symbol):
    """Get AI prediction for a specific stock"""
    stock_data = get_stock_details(symbol)

    if not stock_data:
        return jsonify({"error": "Unable to fetch stock data"}), 404

    prediction = get_stock_prediction(
        symbol,
        stock_data['price'],
        stock_data['change_percent']
    )

    return jsonify(prediction)


@ai_bp.route("/ai/portfolio-insights", methods=['POST'])
def portfolio_insights():
    """Get AI insights for overall portfolio"""
    data = request.get_json()

    total_invested = data.get('total_invested', 0)
    current_value = data.get('current_value', 0)
    total_profit = data.get('total_profit', 0)
    profit_percent = data.get('profit_percent', 0)

    insights = get_portfolio_insights(
        total_invested,
        current_value,
        total_profit,
        profit_percent
    )

    return jsonify(insights)
