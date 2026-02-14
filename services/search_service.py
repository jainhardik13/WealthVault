import requests
import csv
from io import StringIO

NSE_SYMBOLS = []

def load_nse_symbols():
    global NSE_SYMBOLS

    url = "https://archives.nseindia.com/content/equities/EQUITY_L.csv"

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "text/csv"
    }

    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()

    csv_data = csv.DictReader(StringIO(response.text))

    # Extract SYMBOL column
    NSE_SYMBOLS = sorted(row["SYMBOL"] for row in csv_data)


# Load once at startup
load_nse_symbols()


def search_stocks(query):
    query = query.upper().strip()

    if not query:
        return []

    return [s for s in NSE_SYMBOLS if s.startswith(query)][:10]
