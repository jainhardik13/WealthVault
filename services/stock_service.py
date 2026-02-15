"""
Stock Service Module
===================
Handles all stock price fetching and historical data operations.

Supported Exchanges:
- NSE (National Stock Exchange) - Using NSEPython library
- BSE (Bombay Stock Exchange) - Using web scraping/API

Features:
- Real-time stock prices
- Day change and percentage change
- 30-day historical price data
- Caching to prevent redundant API calls
"""

from nsepython import nse_eq
import requests
from bs4 import BeautifulSoup
import zipfile
import io
import csv
from datetime import datetime, timedelta
import time
from models.portfolio_models import get_db_connection, save_history_to_db

# =========================
# IN-MEMORY CACHES
# =========================
# Prevents redundant API calls for same stock within session
HISTORY_CACHE = {}   # Format: { "TCS_2024-01-01": {dates, prices} }


# =========================
# LIVE STOCK PRICE FUNCTIONS
# =========================

def get_stock_details(symbol, exchange='NSE'):
    """
    Fetch real-time stock price, change, and percentage change.

    Args:
        symbol (str): Stock ticker symbol (e.g., 'TCS', 'RELIANCE')
        exchange (str): Stock exchange - 'NSE' or 'BSE' (default: 'NSE')

    Returns:
        dict or None: Stock data containing:
            - price (float): Current market price
            - change (float): Price change from previous close
            - change_percent (float): Percentage change

    Example:
        >>> get_stock_details('TCS', 'NSE')
        {'price': 3500.50, 'change': 25.30, 'change_percent': 0.73}

    Note: Implements 0.3s delay between NSE calls to respect rate limits
    """
    try:
        symbol = symbol.upper()

        if exchange.upper() == 'BSE':
            # ===== BSE STOCK PRICE =====
            return get_bse_stock_price(symbol)
        else:
            # ===== NSE STOCK PRICE (DEFAULT) =====
            data = nse_eq(symbol)
            if not data or "priceInfo" not in data:
                return None

            price_info = data["priceInfo"]

            current_price = float(price_info["lastPrice"])
            prev_close = float(price_info["previousClose"])

            change = round(current_price - prev_close, 2)
            change_percent = round((change / prev_close) * 100, 2)

            # NSE rate-limit safety - wait 0.3 seconds between calls
            time.sleep(0.3)

            return {
                "price": current_price,
                "change": change,
                "change_percent": change_percent
            }

    except Exception as e:
        print(f"Stock price error for {symbol} ({exchange}): {e}")
        return None


def get_bse_stock_price(symbol):
    """
    Fetch BSE stock price using BSE India API.

    BSE uses stock codes instead of symbols (e.g., 532540 for TCS).
    This function fetches price using BSE stock code.

    Args:
        symbol (str): BSE stock code (e.g., '532540' for TCS)

    Returns:
        dict or None: Stock data with price, change, and change_percent

    Note: BSE requires stock codes, not symbols.
          Common BSE codes:
          - TCS = 532540
          - RELIANCE = 500325
          - INFY = 500209
          - HDFC BANK = 500180
    """
    try:
        # BSE API endpoint - getLiveStockData
        url = f"https://api.bseindia.com/BseIndiaAPI/api/StockReach/w?scripcode={symbol}&flag=0&quotetype=EQ&seriesid="

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(url, headers=headers, timeout=5)

        if response.status_code == 200:
            data = response.json()

            if data and 'Data' in data:
                stock_data = data['Data']

                # Extract current price and previous close
                current_price = float(stock_data.get('CurrRate', {}).get('LTP', 0))
                prev_close = float(stock_data.get('PrevClose', 0))

                if current_price == 0 or prev_close == 0:
                    return None

                change = round(current_price - prev_close, 2)
                change_percent = round((change / prev_close) * 100, 2)

                return {
                    "price": current_price,
                    "change": change,
                    "change_percent": change_percent
                }

        return None

    except Exception as e:
        print(f"BSE price error for {symbol}: {e}")
        return None


# =========================
# HISTORICAL PRICE FUNCTIONS
# =========================

def get_stock_history(symbol):
    """
    Retrieve historical stock prices from database.

    Fetches 30-day price history stored in stock_history table.
    Used for generating price charts.

    Args:
        symbol (str): Stock ticker symbol

    Returns:
        dict or None: Historical data containing:
            - dates (list): List of dates (YYYY-MM-DD format)
            - prices (list): Corresponding closing prices

    Example:
        >>> get_stock_history('TCS')
        {
            'dates': ['2024-01-01', '2024-01-02', ...],
            'prices': [3450.50, 3475.20, ...]
        }
    """
    conn = get_db_connection()
    cur = conn.cursor()

    # Retrieve all historical data for this symbol, ordered by date
    cur.execute("""
        SELECT date, close
        FROM stock_history
        WHERE symbol = ?
        ORDER BY date
    """, (symbol,))

    rows = cur.fetchall()
    conn.close()

    if not rows:
        return None

    return {
        "dates": [r[0] for r in rows],
        "prices": [r[1] for r in rows]
    }


def fetch_and_store_history(symbol, exchange='NSE'):
    """
    Fetch and store 30-day historical prices for a stock.

    Downloads historical data from NSE Bhavcopy archives and stores
    in database for chart generation.

    Args:
        symbol (str): Stock ticker symbol
        exchange (str): Stock exchange - currently only NSE supported

    Process:
    1. Loops through last 30 days
    2. Downloads daily Bhavcopy CSV file from NSE
    3. Extracts closing price for the symbol
    4. Saves to stock_history table (INSERT OR IGNORE prevents duplicates)

    Note:
    - BSE historical data fetching not yet implemented
    - NSE data comes from: archives.nseindia.com/content/historical/EQUITIES/
    - Files are in ZIP format containing CSV
    - Skips weekends and holidays (when files are unavailable)
    """
    symbol = symbol.upper()

    # Currently only supports NSE historical data
    if exchange.upper() != 'NSE':
        print(f"Historical data for {exchange} not yet implemented")
        return

    today = datetime.today()
    start = today - timedelta(days=30)  # Go back 30 days

    current = start
    while current <= today:
        # Format date as: 15FEB2024
        date_str = current.strftime("%d%b%Y").upper()
        year = current.strftime("%Y")

        # NSE Bhavcopy URL format
        # Example: https://archives.nseindia.com/content/historical/EQUITIES/2024/cm15FEB2024bhav.csv.zip
        url = (
            f"https://archives.nseindia.com/content/historical/EQUITIES/"
            f"{year}/cm{date_str}bhav.csv.zip"
        )

        try:
            # Download the ZIP file
            r = requests.get(url, timeout=2)
            if r.status_code != 200:
                current += timedelta(days=1)
                continue

            # Extract CSV from ZIP
            z = zipfile.ZipFile(io.BytesIO(r.content))
            csv_name = z.namelist()[0]

            # Parse CSV and find our stock
            with z.open(csv_name) as f:
                reader = csv.DictReader(io.TextIOWrapper(f))
                for row in reader:
                    if row["SYMBOL"] == symbol:
                        # Save closing price to database
                        save_history_to_db(
                            symbol,
                            current.strftime("%Y-%m-%d"),
                            float(row["CLOSE"])
                        )
                        break
        except:
            pass  # Skip days when data unavailable (weekends, holidays)

        current += timedelta(days=1)
