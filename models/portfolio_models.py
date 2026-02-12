import sqlite3
from pathlib import Path

DB_PATH = Path("database/portfolio.db")

def get_db_connection():
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS portfolio (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            buy_price REAL NOT NULL,
            buy_date TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def add_stock(symbol, quantity, buy_price, buy_date):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
                   INSERT INTO portfolio (symbol, quantity, buy_price, buy_date)
        VALUES (?, ?, ?, ?)""", (symbol.upper(), quantity, buy_price, buy_date))

    conn.commit()
    conn.close()

def get_all_stocks():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM portfolio")
    rows = cursor.fetchall()

    conn.close()
    return rows

def delete_stock(stock_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM portfolio WHERE id = ?", (stock_id,))
    conn.commit()
    conn.close()