from src.predict_stat_arb.database.db import get_connection


def fetch_latest_spread(limit=5):
    query = """
        SELECT
            timestamp,
            kalshi_yes_price,
            polymarket_yes_price,
            dem_spread
        FROM house_2026_dem_spread
        ORDER BY timestamp DESC
        LIMIT %s;
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (limit,))
            return cur.fetchall()


def main():
    rows = fetch_latest_spread(limit=5)

    for timestamp, kalshi_price, polymarket_price, spread in rows:
        print(
            f"{timestamp} | "
            f"Kalshi: {kalshi_price} | "
            f"Polymarket: {polymarket_price} | "
            f"Spread: {spread}"
        )
    

if __name__ == "__main__":
    main()
