from pathlib import Path
import pandas as pd
import ast
from datetime import datetime
import argparse

from src.predict_stat_arb.ingestion.polymarket_client import PolymarketClient

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=5)
    args = parser.parse_args()

    client = PolymarketClient()

    project_root = Path(__file__).resolve().parents[3]
    markets_path = project_root / "data/raw/polymarket_markets_latest.csv"

    markets_df = pd.read_csv(markets_path)

    price_frames = []

    for _, row in markets_df.head(args.limit).iterrows():
        token_ids = ast.literal_eval(row["clobTokenIds"])

        for token in token_ids:
            history_df = client.get_price_history(token)
            history_df["market_id"] = row["id"]

            price_frames.append(history_df)

    prices_df = pd.concat(price_frames, ignore_index=True)

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

    output_path = (
        project_root
        / "data/raw"
        / f"polymarket_prices_{timestamp}.csv"
    )

    latest_path = (
        project_root
        / "data/raw"
        / "polymarket_prices_latest.csv"
    )

    prices_df.to_csv(output_path, index=False)
    prices_df.to_csv(latest_path, index=False)

    print(f"Saved {len(prices_df)} rows of price history")


if __name__ == "__main__":
    main()