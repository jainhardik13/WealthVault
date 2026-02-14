from flask import Blueprint, request, jsonify
from services.search_service import search_stocks

search_bp = Blueprint("search", __name__)

@search_bp.route("/search")
def search():
    query = request.args.get("q", "")
    print("SEARCH QUERY:", query)  # Debug log
    result = search_stocks(query)
    print(result)
    return jsonify(result)