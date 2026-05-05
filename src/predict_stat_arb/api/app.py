from fastapi import FastAPI


app = FastAPI(title="Prediction Market Spread API")


@app.get("/health")
def health():
    return {"status": "ok"}

from fastapi import FastAPI

from src.predict_stat_arb.database.query_spread import fetch_latest_spread


app = FastAPI(title="Prediction Market Spread API")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/spread/latest")
def latest_spread():
    rows = fetch_latest_spread(limit=1)

    if not rows:
        return {"data": None}

    timestamp, kalshi_price, polymarket_price, spread = rows[0]

    return {
        "timestamp": timestamp.isoformat(),
        "kalshi_yes_price": float(kalshi_price),
        "polymarket_yes_price": float(polymarket_price),
        "dem_spread": float(spread),
    }
@app.get("/spread/history")

def spread_history(limit: int = 100):
    rows = fetch_latest_spread(limit=limit)

    return [
        {
            "timestamp": timestamp.isoformat(),
            "kalshi_yes_price": float(kalshi_price),
            "polymarket_yes_price": float(polymarket_price),
            "dem_spread": float(spread),
        }
        for timestamp, kalshi_price, polymarket_price, spread in rows
    ]
