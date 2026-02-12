from nsepython import nse_eq, nse_fno
import time

# Cache F&O symbols (loaded once)
FNO_SYMBOLS = set()

def load_fno_symbols():
    global FNO_SYMBOLS
    try:
        data = nse_fno()
        for item in data:
            FNO_SYMBOLS.add(item["symbol"])
    except Exception:
        pass


# Load once at startup
load_fno_symbols()


def get_stock_details(symbol):
    try:
        symbol = symbol.upper()

        # Quick validation: equity OR F&O
        if symbol not in FNO_SYMBOLS:
            # Not F&O, but still may be equity — allow once
            data = nse_eq(symbol)
        else:
            # F&O stocks are heavily traded → faster response
            data = nse_eq(symbol)

        if not data or "priceInfo" not in data:
            return None

        price_info = data["priceInfo"]

        current_price = float(price_info["lastPrice"])
        prev_close = float(price_info["previousClose"])

        change = round(current_price - prev_close, 2)
        change_percent = round((change / prev_close) * 100, 2)

        time.sleep(0.3)  # Reduced delay

        return {
            "price": current_price,
            "change": change,
            "change_percent": change_percent
        }

    except Exception as e:
        print(f"NSE fetch error for {symbol}: {e}")
        return None
