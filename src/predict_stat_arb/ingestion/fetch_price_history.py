from pathlib import Path
import pandas as pd
import ast
from datetime import datetime
import argparse

from src.predict_stat_arb.ingestion.polymarket_client import PolymarketClient

def fetch_polymarket_price_history(
    token_id,
    market_id=None,
    output_dir=None,
    label="polymarket_prices",
):
    client = PolymarketClient()

    history_df = client.get_price_history(token_id)

    if market_id is not None:
        history_df["market_id"] = market_id

    project_root = Path(__file__).resolve().parents[3]

    if output_dir is None:
        output_dir = project_root / "data" / "raw"
    else:
        output_dir = Path(output_dir)

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

    output_path = output_dir / f"{label}_{timestamp}.csv"
    latest_path = output_dir / f"{label}_latest.csv"

    history_df.to_csv(output_path, index=False)
    history_df.to_csv(latest_path, index=False)

    print(f"Saved {len(history_df)} rows of Polymarket price history")

    return latest_path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--token-id", type=str, default=None)
    parser.add_argument("--label", type=str, default="polymarket_prices")

    args = parser.parse_args()

    if args.token_id is not None:
        fetch_polymarket_price_history(
            token_id=args.token_id,
            label=args.label,
        )
        return

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