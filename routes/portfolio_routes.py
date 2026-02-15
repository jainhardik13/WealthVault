"""
Portfolio Routes Module
======================
Handles all portfolio-related HTTP routes and business logic.

Routes:
- /dashboard (GET/POST) - Main portfolio dashboard with add stock form
- /edit/<stock_id> (GET/POST) - Edit existing stock entry
- /delete/<stock_id> (GET) - Delete stock from portfolio

Features:
- CRUD operations for stock portfolio
- Real-time price updates
- Profit/loss calculations
- Portfolio summary statistics
- Input validation and error handling
- Flash messages for user feedback
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.portfolio_models import add_stock, get_all_stocks, delete_stock, get_stock_by_id, update_stock
from services.stock_service import get_stock_details
from services.stock_service import fetch_and_store_history

# Create Flask Blueprint for modular routing
portfolio_bp = Blueprint('portfolio', __name__)


@portfolio_bp.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    """
    Main portfolio dashboard route.

    GET: Display all stocks with live prices and portfolio summary
    POST: Add new stock to portfolio

    Form Fields (POST):
    - symbol: Stock ticker (e.g., TCS, RELIANCE, or BSE code like 532540)
    - quantity: Number of shares
    - buy_price: Purchase price per share
    - buy_date: Date of purchase (YYYY-MM-DD)
    - exchange: NSE or BSE (default: NSE)

    Returns:
        Rendered dashboard.html with:
        - stocks: List of portfolio stocks with live data
        - summary: Portfolio totals (invested, current value, profit/loss)
    """
    if request.method == 'POST':
        try:
            # ===== Extract and validate form data =====
            symbol = request.form.get('symbol', '').strip()
            quantity = request.form.get('quantity', '')
            buy_price = request.form.get('buy_price', '')
            buy_date = request.form.get('buy_date', '')
            exchange = request.form.get('exchange', 'NSE').strip()  # Get exchange selection

            # Validation: Stock symbol required
            if not symbol:
                flash('Stock symbol is required', 'error')
                return redirect(url_for('portfolio.dashboard'))

            # Validation: Quantity must be positive integer
            if not quantity or int(quantity) <= 0:
                flash('Quantity must be greater than 0', 'error')
                return redirect(url_for('portfolio.dashboard'))

            # Validation: Buy price must be positive number
            if not buy_price or float(buy_price) <= 0:
                flash('Buy price must be greater than 0', 'error')
                return redirect(url_for('portfolio.dashboard'))

            # Validation: Buy date required
            if not buy_date:
                flash('Buy date is required', 'error')
                return redirect(url_for('portfolio.dashboard'))

            # ===== Verify stock exists before adding =====
            stock_data = get_stock_details(symbol, exchange)
            if not stock_data:
                flash(f'Stock symbol "{symbol}" not found on {exchange}. Please verify the symbol.', 'error')
                return redirect(url_for('portfolio.dashboard'))

            # ===== Add stock to database =====
            add_stock(symbol, int(quantity), float(buy_price), buy_date, exchange)

            # ===== Fetch historical data for charts (NSE only for now) =====
            if exchange.upper() == 'NSE':
                fetch_and_store_history(symbol, exchange)

            flash(f'Successfully added {symbol} ({exchange}) to your portfolio!', 'success')
            return redirect(url_for('portfolio.dashboard'))

        except ValueError as e:
            flash('Invalid input. Please check quantity and price values.', 'error')
            return redirect(url_for('portfolio.dashboard'))
        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'error')
            return redirect(url_for('portfolio.dashboard'))

    # ===== GET REQUEST: Display portfolio =====
    stocks = get_all_stocks()
    portfolio_data = []

    # Initialize portfolio totals
    total_invested = 0
    total_current_value = 0

    # ===== Process each stock to get live prices =====
    for stock in stocks:
        try:
            # Get exchange from database (defaults to NSE if not set)
            # sqlite3.Row doesn't have .get() method, use try/except
            try:
                exchange = stock['exchange'] if stock['exchange'] else 'NSE'
            except (KeyError, IndexError):
                exchange = 'NSE'

            # Fetch live price from respective exchange
            live = get_stock_details(stock['symbol'], exchange)

            if live:
                # Calculate profit/loss
                invested = stock['buy_price'] * stock['quantity']
                current_value = live['price'] * stock['quantity']
                profit = round(current_value - invested, 2)
                percent = round((profit / invested) * 100, 2)

                # Add to portfolio totals
                total_invested += invested
                total_current_value += current_value

                portfolio_data.append({
                    "id": stock['id'],
                    "symbol": stock['symbol'],
                    "exchange": exchange,  # Include exchange info
                    "quantity": stock['quantity'],
                    "buy_price": stock['buy_price'],
                    "buy_date": stock['buy_date'],
                    "current_price": live['price'],
                    "profit": profit,
                    "percent": percent
                })
            else:
                # If live price unavailable, still show the stock with N/A values
                portfolio_data.append({
                    "id": stock['id'],
                    "symbol": stock['symbol'],
                    "exchange": exchange,
                    "quantity": stock['quantity'],
                    "buy_price": stock['buy_price'],
                    "buy_date": stock['buy_date'],
                    "current_price": "N/A",
                    "profit": "N/A",
                    "percent": "N/A"
                })
        except Exception as e:
            print(f"Error processing stock {stock['symbol']}: {e}")
            continue

    # ===== Calculate overall portfolio summary =====
    total_profit = round(total_current_value - total_invested, 2)
    total_percent = round((total_profit / total_invested) * 100, 2) if total_invested > 0 else 0

    summary = {
        "total_invested": round(total_invested, 2),
        "total_current_value": round(total_current_value, 2),
        "total_profit": total_profit,
        "total_percent": total_percent
    }

    return render_template("dashboard.html", stocks=portfolio_data, summary=summary)


@portfolio_bp.route("/delete/<int:stock_id>")
def delete(stock_id):
    """
    Delete a stock from the portfolio.

    Args:
        stock_id (int): Database ID of the stock to delete

    Returns:
        Redirect to dashboard with success/error message
    """
    try:
        stock = get_stock_by_id(stock_id)
        if stock:
            delete_stock(stock_id)
            flash(f'Successfully deleted {stock["symbol"]} from portfolio', 'success')
        else:
            flash('Stock not found', 'error')
    except Exception as e:
        flash(f'Error deleting stock: {str(e)}', 'error')

    return redirect(url_for('portfolio.dashboard'))


@portfolio_bp.route("/edit/<int:stock_id>", methods=['GET', 'POST'])
def edit(stock_id):
    """
    Edit an existing stock entry.

    GET: Display edit form pre-filled with current stock data
    POST: Update stock with new values

    Args:
        stock_id (int): Database ID of the stock to edit

    Returns:
        GET: Rendered edit_stock.html template
        POST: Redirect to dashboard with success/error message
    """
    if request.method == 'POST':
        try:
            # ===== Extract and validate form data =====
            symbol = request.form.get('symbol', '').strip()
            quantity = request.form.get('quantity', '')
            buy_price = request.form.get('buy_price', '')
            buy_date = request.form.get('buy_date', '')
            exchange = request.form.get('exchange', 'NSE').strip()  # Get exchange selection

            # Validation: Stock symbol required
            if not symbol:
                flash('Stock symbol is required', 'error')
                return redirect(url_for('portfolio.edit', stock_id=stock_id))

            # Validation: Quantity must be positive
            if not quantity or int(quantity) <= 0:
                flash('Quantity must be greater than 0', 'error')
                return redirect(url_for('portfolio.edit', stock_id=stock_id))

            # Validation: Buy price must be positive
            if not buy_price or float(buy_price) <= 0:
                flash('Buy price must be greater than 0', 'error')
                return redirect(url_for('portfolio.edit', stock_id=stock_id))

            # Validation: Buy date required
            if not buy_date:
                flash('Buy date is required', 'error')
                return redirect(url_for('portfolio.edit', stock_id=stock_id))

            # ===== Update stock in database =====
            update_stock(stock_id, symbol, int(quantity), float(buy_price), buy_date, exchange)
            flash(f'Successfully updated {symbol} ({exchange})', 'success')
            return redirect(url_for('portfolio.dashboard'))

        except ValueError:
            flash('Invalid input. Please check quantity and price values.', 'error')
            return redirect(url_for('portfolio.edit', stock_id=stock_id))
        except Exception as e:
            flash(f'Error updating stock: {str(e)}', 'error')
            return redirect(url_for('portfolio.edit', stock_id=stock_id))

    # ===== GET REQUEST: Display edit form =====
    stock = get_stock_by_id(stock_id)
    if not stock:
        flash('Stock not found', 'error')
        return redirect(url_for('portfolio.dashboard'))

    return render_template('edit_stock.html', stock=stock)