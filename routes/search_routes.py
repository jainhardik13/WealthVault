from flask import Blueprint, request, jsonify
from services.search_service import search_stocks
from services.stock_service import get_stock_details

search_bp = Blueprint("search", __name__)

@search_bp.route("/search")
def search():
    query = request.args.get("q", "")
    print("SEARCH QUERY:", query)  # Debug log
    result = search_stocks(query)
    print(result)
    return jsonify(result)


@search_bp.route("/stock/live/<symbol>")
def get_live_price(symbol):
    """Get live stock price for search feature"""
    stock_data = get_stock_details(symbol)

    if stock_data:
        return jsonify({
            "success": True,
            "symbol": symbol,
            "price": stock_data['price'],
            "change": stock_data['change'],
            "change_percent": stock_data['change_percent']
        })
    else:
        return jsonify({
            "success": False,
            "error": "Unable to fetch stock data"
        }), 404