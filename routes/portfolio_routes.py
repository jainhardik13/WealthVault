from flask import Blueprint, render_template, request, redirect, url_for
from models.portfolio_models import add_stock, get_all_stocks, delete_stock
from services.stock_service import get_stock_details

portfolio_bp = Blueprint('portfolio', __name__)

@portfolio_bp.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if request.method == 'POST':
        symbol = request.form['symbol']
        quantity = int(request.form['quantity'])
        buy_price = float(request.form['buy_price'])
        buy_date = request.form['buy_date']

        add_stock(symbol, quantity, buy_price, buy_date)
        return redirect(url_for('portfolio.dashboard'))

    stocks = get_all_stocks()
    portfolio_data = []

    for stock in stocks:
        live = get_stock_details(stock['symbol'])

        if live:
            invested = stock['buy_price'] * stock['quantity']
            current_value = live['price'] * stock['quantity']
            profit = round(current_value - invested, 2)
            percent = round((profit / invested) * 100, 2)

            portfolio_data.append({
                "id": stock['id'],
                "symbol": stock['symbol'],
                "quantity": stock['quantity'],
                "buy_price": stock['buy_price'],
                "current_price": live['price'],
                "profit": profit,
                "percent": percent
            })

    return render_template("dashboard.html", stocks=portfolio_data)

@portfolio_bp.route("/delete/<int:stock_id>")
def delete(stock_id):
    delete_stock(stock_id)
    return redirect(url_for('portfolio.dashboard'))