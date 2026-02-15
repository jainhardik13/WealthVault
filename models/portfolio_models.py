"""
Portfolio Database Model
========================
This module handles all database operations for the stock portfolio.

Database Structure:
1. portfolio table - Stores user's stock holdings
2. stock_history table - Stores historical prices for charts

Uses SQLite for lightweight, serverless database storage.
"""

import sqlite3
from pathlib import Path

# Database file path - stored in 'database' folder
DB_PATH = Path("database/portfolio.db")
print("USING DATABASE:", DB_PATH)


# =========================
# DATABASE CONNECTION
# =========================

def get_db_connection():
    """
    Establishes connection to SQLite database.

    Features:
    - Creates 'database' directory if it doesn't exist
    - Returns Row objects (dict-like access) instead of tuples

    Returns:
        sqlite3.Connection: Database connection object
    """
    DB_PATH.parent.mkdir(exist_ok=True)  # Create database folder if needed
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Enable column access by name
    return conn


# =========================
# DATABASE INITIALIZATION
# =========================

def init_db():
    """
    Creates database tables if they don't exist.
    Safe to call multiple times (uses IF NOT EXISTS).

    Tables Created:
    1. portfolio - User's stock holdings
       - id: Auto-incrementing primary key
       - symbol: Stock ticker (e.g., TCS, RELIANCE)
       - quantity: Number of shares owned
       - buy_price: Purchase price per share
       - buy_date: Date of purchase
       - exchange: Stock exchange (NSE or BSE)

    2. stock_history - Historical price data for charts
       - symbol: Stock ticker
       - date: Trading date
       - close: Closing price on that date
       - Composite primary key (symbol, date) prevents duplicates
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Portfolio table - stores user's stock holdings
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS portfolio (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            buy_price REAL NOT NULL,
            buy_date TEXT NOT NULL,
            exchange TEXT DEFAULT 'NSE'
        )
    """)

    # Stock history table - stores historical prices for graph generation
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stock_history (
            symbol TEXT NOT NULL,
            date TEXT NOT NULL,
            close REAL NOT NULL,
            PRIMARY KEY (symbol, date)
        )
    """)

    conn.commit()
    conn.close()


# =========================
# PORTFOLIO OPERATIONS (CRUD)
# =========================

def add_stock(symbol, quantity, buy_price, buy_date, exchange='NSE'):
    """
    Add a new stock to the portfolio.

    Args:
        symbol (str): Stock ticker symbol (e.g., 'TCS', 'RELIANCE')
        quantity (int): Number of shares
        buy_price (float): Purchase price per share
        buy_date (str): Date of purchase (YYYY-MM-DD format)
        exchange (str): Stock exchange - 'NSE' or 'BSE' (default: 'NSE')

    Note: Symbol is automatically converted to uppercase for consistency
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO portfolio (symbol, quantity, buy_price, buy_date, exchange)
        VALUES (?, ?, ?, ?, ?)
    """, (symbol.upper(), quantity, buy_price, buy_date, exchange.upper()))

    conn.commit()
    conn.close()


def get_all_stocks():
    """
    Retrieve all stocks from the portfolio.

    Returns:
        list[sqlite3.Row]: List of all portfolio entries
                          Each row can be accessed like a dictionary
                          Example: row['symbol'], row['quantity']
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM portfolio")
    rows = cursor.fetchall()

    conn.close()
    return rows


def delete_stock(stock_id):
    """
    Delete a stock from the portfolio by its ID.

    Args:
        stock_id (int): Database ID of the stock to delete
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM portfolio WHERE id = ?", (stock_id,))
    conn.commit()
    conn.close()


def get_stock_by_id(stock_id):
    """
    Retrieve a single stock entry by its ID.

    Args:
        stock_id (int): Database ID of the stock

    Returns:
        sqlite3.Row or None: Stock data if found, None otherwise
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM portfolio WHERE id = ?", (stock_id,))
    row = cursor.fetchone()

    conn.close()
    return row


def update_stock(stock_id, symbol, quantity, buy_price, buy_date, exchange='NSE'):
    """
    Update an existing stock entry.

    Args:
        stock_id (int): Database ID of the stock to update
        symbol (str): Updated stock ticker
        quantity (int): Updated quantity
        buy_price (float): Updated purchase price
        buy_date (str): Updated purchase date
        exchange (str): Stock exchange - 'NSE' or 'BSE'
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE portfolio
        SET symbol = ?, quantity = ?, buy_price = ?, buy_date = ?, exchange = ?
        WHERE id = ?
    """, (symbol.upper(), quantity, buy_price, buy_date, exchange.upper(), stock_id))

    conn.commit()
    conn.close()


# =========================
# STOCK HISTORY OPERATIONS
# =========================

def save_history_to_db(symbol, date, close):
    """
    Save historical closing price for a stock.
    Used for generating price charts.

    Args:
        symbol (str): Stock ticker
        date (str): Trading date (YYYY-MM-DD)
        close (float): Closing price on that date

    Note: Uses INSERT OR IGNORE to prevent duplicate entries
          Composite primary key (symbol, date) ensures uniqueness
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO stock_history (symbol, date, close)
        VALUES (?, ?, ?)
    """, (symbol.upper(), date, close))

    conn.commit()
    conn.close()
