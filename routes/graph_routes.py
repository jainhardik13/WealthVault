from flask import Blueprint, request, jsonify
from services.stock_service import get_stock_history

graph_bp = Blueprint('graph', __name__)

@graph_bp.route("/stock/history/<symbol>")
def stock_history(symbol):
    data = get_stock_history(symbol)
    return jsonify(data)