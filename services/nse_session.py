import requests
from flask import session

session = requests.session()

def init_nse_session():
    """Hit NSE homepage once to get cookies"""

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html",
        "Referer": "https://www.nseindia.com/"
    }

    session.get("https://www.nseindia.com/", headers=headers, timeout=10)

    return session